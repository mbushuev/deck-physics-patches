"""Generate the checked game-specific payload from the local installation."""

from hashlib import file_digest
from pathlib import Path
import shutil
import subprocess
import sys

prefix, executable = map(Path, sys.argv[1:])
game = executable.parent
core = (prefix / 'pfx/drive_c/Program Files (x86)/NVIDIA Corporation/PhysX'
        / 'Engine/v2.8.3/PhysXCore.dll')
source = Path(__file__).resolve().parent
output = source / 'generated'
output.mkdir()
subprocess.run([sys.executable, '-B', str(source / 'perfmon.py'), str(output),
                str(game / 'APEX_release.dll'), str(core)], check=True)
shutil.copyfile(game / 'APEX_Clothing.dll', output / 'APEX_Clothing.dll')

expected = {
    'APEX_release.dll': '6aa581c74165607645008d66a551e75f34ab0a96ff736705aec3ee130202bdd5',
    'PhysXCore.dll': '05d62d690d16433a03816d25a2bb138c1994c8279ee5710e8e8b2eccb6f4a226',
    'APEX_Clothing.dll': 'b2d98a666e0e70779048dad3b6ffb715b048245bd4611af6344e879d283f5f15',
}
for name, digest in expected.items():
    with (output / name).open('rb') as file:
        if file_digest(file, 'sha256').hexdigest() != digest:
            raise ValueError(f'Generated {name} differs from the validated build.')
