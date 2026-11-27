"""Check that the staged Mafia II benchmark uses the installed CRC instructions."""
from hashlib import sha256
from pathlib import Path
import struct
import sys

CRC_RANGES = ((0xE57AA0, 0xE57ADA), (0xE57B30, 0xE57B6A), (0xE57C50, 0xE57E8C))

def crc_instructions(path):
    data = path.read_bytes()
    pe, = struct.unpack_from("<I", data, 0x3c)
    if data[:2] != b"MZ" or data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("Invalid PE header")
    count, = struct.unpack_from("<H", data, pe + 6)
    optional_size, = struct.unpack_from("<H", data, pe + 20)
    image_base, = struct.unpack_from("<I", data, pe + 52)
    table = pe + 24 + optional_size
    for index in range(count):
        name, size, rva, length, offset = struct.unpack_from("<8s4I", data, table + 40 * index)
        if name == b".text\0\0\0":
            section_va = image_base + rva
            if offset + length > len(data):
                raise ValueError("Invalid CRC section extent")
            if not all(section_va <= start < end <= section_va + min(size, length)
                       for start, end in CRC_RANGES):
                raise ValueError("Expected CRC instructions within executable .text")
            return tuple(data[offset + start - section_va:offset + end - section_va]
                         for start, end in CRC_RANGES)
    raise ValueError("Executable has no .text section")

reference, candidate = map(Path, sys.argv[1:3])
crc = crc_instructions(candidate)
if crc_instructions(reference) != crc:
    raise SystemExit("The staged image changes the installed CRC instructions.")
print("Installed CRC instructions verified:", sha256(b"".join(crc)).hexdigest())
