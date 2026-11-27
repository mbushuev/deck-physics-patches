"""Create a private test copy of the exact Mafia II executable."""
import hashlib
import json
from pathlib import Path
import struct
import sys

base = Path(__file__).resolve().parent
source, destination = map(Path, sys.argv[1:])
data = bytearray(source.read_bytes())
original = '497ed7017f2a355b73fbb20940f1b729d06f5740d7e07c45399d77449382deb1'
assert hashlib.sha256(data).hexdigest() == original
header, = struct.unpack_from('<I', data, 0x3c)
optional = header + 24
sections = optional + struct.unpack_from('<H', data, header + 20)[0]
count, = struct.unpack_from('<H', data, header + 6)
image_base, = struct.unpack_from('<I', data, optional + 28)
assert image_base == 0x400000 and struct.unpack_from('<II', data, optional + 96 + 5 * 8) == (0, 0)
indexed = [struct.unpack_from('<IIII', data, sections + i * 40 + 8)
           for i in range(count)]

def offset(address, size):
    rva = address - image_base
    for _, start, length, raw in indexed:
        if start <= rva and rva + size <= start + length:
            return raw + rva - start
    raise ValueError(f'Unmapped virtual address {address:#x}')

assert struct.unpack_from('<d', data, offset(0x18f1430, 8)) == (.5,)
assert struct.unpack_from('<d', data, offset(0x1903a78, 8)) == (127.5,)
stats = []
for name, start, stop in (('position', 0x579a60, 0x579b4b), ('basis', 0x57ad46, 0x57aee6)):
    region = stop - start
    blob = (base / f'{name}.bin').read_bytes()
    assert 0 < len(blob) <= region
    loc = offset(start, region)
    data[loc:loc + region] = blob.ljust(region, b'\x90')
    stats.append({'section': name, 'address': hex(start), 'bytes': len(blob), 'original_bytes': region})
struct.pack_into('<I', data, optional + 64, 0)
destination.write_bytes(data)
print(json.dumps({'source_sha256': original, 'patched_sha256': hashlib.sha256(data).hexdigest(),
                  'regions': stats}, indent=2))
