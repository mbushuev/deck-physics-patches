"""Prepare Mafia II's validated render packing for this local Steam build."""

from hashlib import sha256
from struct import pack_into, unpack_from


GAME_SHA256 = '497ed7017f2a355b73fbb20940f1b729d06f5740d7e07c45399d77449382deb1'
PACKED_SHA256 = '86f265f825f421a8d3df15666ffc152c006d9b1bc26578b5a59d4e810b32b740'
POSITION = 0x579a60
BASIS = 0x57ad10
POSITION_CALLS = (
    0x133b70d, 0x140d4f4, 0x14cf493, 0x15bc07b, 0x15bc82f, 0x15bcad6,
    0x15bcdf3, 0x15bd306, 0x15bd594, 0x1674c2f, 0x167557f, 0x167fdab,
    0x167fdd8, 0x16d58be, 0x16d58db, 0x16d58f1, 0x16d5a66, 0x16d5b79,
    0x16d5c85, 0x16d5d8a, 0x16d6c12,
)
BASIS_CALLS = (
    0x1674950, 0x1674b3c, 0x16d5f5d, 0x16d5f8f, 0x16d5fbf, 0x16d5fea,
    0x16d6d37,
)


def aligned(size, alignment):
    return (size + alignment - 1) // alignment * alignment


def write_displacement(image, field, address, destination):
    pack_into('<i', image, field, destination - address)


def build_render_image(executable, assets):
    image = bytearray(executable.read_bytes())
    if sha256(image).hexdigest() != GAME_SHA256:
        raise ValueError('GPU Clothing requires the supported Steam build of Mafia II Classic.')

    pe, = unpack_from('<I', image, 0x3c)
    coff = pe + 4
    optional = coff + 20
    count, = unpack_from('<H', image, coff + 2)
    optional_size, = unpack_from('<H', image, coff + 16)
    base, section_alignment, file_alignment = unpack_from('<III', image, optional + 28)
    table = optional + optional_size
    sections = {}
    for i in range(count):
        name, size, rva, file_size, offset = unpack_from('<8sIIII', image, table + 40 * i)
        sections[name.rstrip(b'\0')] = (size, rva, file_size, offset)

    header = table + count * 40
    if image[header:header + 40] != b'\0' * 40:
        raise ValueError('The game PE header has no room for the renderer section.')
    code_rva = aligned(max(rva + max(size, file_size)
                           for size, rva, file_size, _ in sections.values()), section_alignment)
    code_offset = aligned(len(image), file_alignment)
    position_code = (assets / 'position.bin').read_bytes()
    basis_tail = (assets / 'basis.bin').read_bytes()
    if len(position_code) != 121 or len(basis_tail) != 221:
        raise ValueError('The renderer code does not match the validated build.')

    # Keep the original basis prologue and relocate its one external call.
    _, text_rva, _, text_offset = sections[b'.text']
    basis_offset = text_offset + BASIS - base - text_rva
    prologue = image[basis_offset:basis_offset + 0x36]
    basis_address = base + code_rva + aligned(235, 16)
    call_offset = 0x57ad25 - BASIS
    write_displacement(prologue, call_offset + 1, basis_address + call_offset + 5, 0x41b350)
    code = (position_code.ljust(235, b'\x90').ljust(aligned(235, 16), b'\xcc')
            + (prologue + basis_tail).ljust(470, b'\x90'))

    # The render call sites use the accelerated copies. The stock routines and
    # all original sections apart from the render call displacements stay intact.
    _, renderer_rva, _, renderer_offset = sections[b'.textnc']
    for calls, source, target in ((POSITION_CALLS, POSITION, base + code_rva),
                                  (BASIS_CALLS, BASIS, basis_address)):
        for address in calls:
            field = renderer_offset + address - base - renderer_rva
            displacement, = unpack_from('<i', image, field + 1)
            if image[field] not in (0xe8, 0xe9) or address + 5 + displacement != source:
                raise ValueError('An expected Mafia II renderer call is missing.')
            write_displacement(image, field + 1, address + 5, target)

    raw_size = aligned(len(code), file_alignment)
    pack_into('<8sIIIIIIHHI', image, header, b'.dpmesh', len(code), code_rva,
              raw_size, code_offset, 0, 0, 0, 0, 0x60000020)
    pack_into('<H', image, coff + 2, count + 1)
    pack_into('<I', image, optional + 56, aligned(code_rva + len(code), section_alignment))
    image.extend(b'\0' * (code_offset - len(image)))
    image.extend(code.ljust(raw_size, b'\0'))

    if sha256(image).hexdigest() != PACKED_SHA256:
        raise ValueError('The generated Mafia II renderer differs from the validated build.')
    return image
