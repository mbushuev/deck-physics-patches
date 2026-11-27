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
def run(script, *args):
    subprocess.run([sys.executable, '-B', str(source / script), *map(str, args)], check=True)

run('packing.py', executable, output / 'mafia2.exe')
run('perfmon.py', output, game / 'APEX_release.dll', core)
run('check-crc.py', executable, output / 'mafia2.exe')
shutil.copyfile(game / 'APEX_Clothing.dll', output / 'APEX_Clothing.dll')

expected = {
    'mafia2.exe': 'b4185920ba7617cbde7cee1c08b7deaf953af18d3083c0286ce927ff5f2f1aca',
    'APEX_release.dll': '6aa581c74165607645008d66a551e75f34ab0a96ff736705aec3ee130202bdd5',
    'PhysXCore.dll': '05d62d690d16433a03816d25a2bb138c1994c8279ee5710e8e8b2eccb6f4a226',
    'APEX_Clothing.dll': 'b2d98a666e0e70779048dad3b6ffb715b048245bd4611af6344e879d283f5f15',
}
for name, digest in expected.items():
    with (output / name).open('rb') as file:
        if file_digest(file, 'sha256').hexdigest() != digest:
            raise ValueError(f'Generated {name} differs from the validated build.')
