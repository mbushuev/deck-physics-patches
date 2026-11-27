"""Guard legacy performance event emission before collecting inactive event metadata."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys

module_defs={
    'APEX_release.dll': (
        '2ed59ea51b7daea25f409ab2b9d9620178448f9e8240cdedcb52ea50329f54eb',
        0x828f4, (0x613e0,0x61480)),
    'PhysXCore.dll': (
        '76968970b39c7201352efd133063771924a10c69b1f6847922d25c62a48347fc',
        0x251120, (0xf9380,0xf9420)),
}
def align(value,block):
    assert block>0 and not (block & (block-1))
    return (value+block-1)&-block

def pack_jump(source,target):
    return b'\xe9'+struct.pack('<i',target-source-5)

def make_patch(source,out):
    known,flag,entries=module_defs[source.name]
    data=bytearray(source.read_bytes())
    original_digest=sha256(data).hexdigest()
    known_bases={known}
    if source.name=='PhysXCore.dll':
        known_bases.add('64fe5eeeb27670b9e8231e0e1c0cd01eef4b3b30e85216744ec6d83e0156419a')
    assert original_digest in known_bases,source.name
    pe=struct.unpack_from('<I',data,0x3c)[0]
    assert data[pe:pe+4]==b'PE\0\0'
    machine,count=struct.unpack_from('<HH',data,pe+4)
    opt_size=struct.unpack_from('<H',data,pe+20)[0]
    opt=pe+24
    assert machine==0x14c and struct.unpack_from('<H',data,opt)[0]==0x10b
    opt_end=opt+opt_size
    image_align,file_align=struct.unpack_from('<II',data,opt+32)
    size_image,size_headers=struct.unpack_from('<II',data,opt+56)
    section_table=opt_end
    next_section=section_table+count*40
    assert next_section+40<=size_headers and not any(data[next_section:next_section+40])
    sections=[struct.unpack_from('<4I',data,section_table+i*40+8) for i in range(count)]
    assert all(align(v+max(vs,rawsize),image_align)<=size_image for vs,v,rawsize,_ in sections)
    def offset(va):
        return next(raw+va-v for vs,v,rawsize,raw in sections if v<=va<v+min(vs,rawsize))
    base_va=struct.unpack_from('<I',data,opt+28)[0]
    payload=bytearray()
    edits=[]
    for entry in entries:
        original=bytes(data[offset(entry):offset(entry)+5])
        assert original==bytes.fromhex('83ec245356')
        assert bytes.fromhex('833d')+struct.pack('<I',base_va+flag)+b'\0' in data[offset(entry):offset(entry)+150]
        stub_va=size_image+len(payload)
        # Keep both incoming EAX and the original active-mode entry unchanged.
        # CALL/POP gets the current instruction address under image relocation.
        pc=stub_va+6
        stub=(b'\x50\xe8\0\0\0\0\x58\x83\xb8'+struct.pack('<i',flag-pc)
              +b'\x00\x58\x75\x03\xc2\x08\x00'+original)
        stub+=pack_jump(stub_va+len(stub),entry+len(original))
        data[offset(entry):offset(entry)+5]=pack_jump(entry,stub_va)
        payload.extend(stub)
        edits.append(dict(entry=hex(entry),stub=hex(stub_va)))
    old_cert_start,old_cert_size=struct.unpack_from('<II',data,opt+96+4*8)
    if old_cert_size:
        end=old_cert_start+old_cert_size
        assert end<=len(data)
        assert not any(raw<end and old_cert_start<raw+n for _,_,n,raw in sections)
        if end==len(data):
            del data[old_cert_start:]
        struct.pack_into('<II',data,opt+96+4*8,0,0)
    start=align(len(data),file_align)
    raw_size=align(len(payload),file_align)
    data.extend(bytes(start-len(data))+payload+bytes(raw_size-len(payload)))
    struct.pack_into('<8s6I2HI',data,next_section,b'.perfmon',len(payload),size_image,raw_size,start,0,0,0,0,0x60000020)
    struct.pack_into('<H',data,pe+6,count+1)
    size_code=struct.unpack_from('<I',data,opt+4)[0]
    struct.pack_into('<I',data,opt+4,size_code+raw_size)
    struct.pack_into('<I',data,opt+56,align(size_image+len(payload),image_align))
    struct.pack_into('<I',data,opt+64,0)
    out.write_bytes(data)
    return dict(module=source.name,original=original_digest,candidate=sha256(data).hexdigest(),
                guard=hex(flag),functions=edits)
output=Path(sys.argv[1])
output.mkdir(parents=True,exist_ok=True)
results=[make_patch(source,output/source.name) for source in map(Path,sys.argv[2:])]
(output/'build.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
