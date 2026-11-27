"""Build the GPU Clothing archive for the Deck Physics installer."""

from pathlib import Path
import subprocess
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


SOURCE = Path(__file__).resolve().parent
OUTPUT = SOURCE.parents[1] / 'patches/mafia-ii-classic/gpu-clothing.deckphysx.zip'


def build(output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        work = Path(directory)
        library = work / 'mafia-gpu-clothing.so'
        subprocess.run(['cc', '-O2', '-Wall', '-Wextra', '-fPIC', '-shared', '-pthread',
                        '-Wl,--build-id=none', '-o', str(library), 'cloth-route.c', 'fill.c', '-ldl'],
                       cwd=SOURCE, check=True)
        packing = work / 'packing.o'
        subprocess.run(['as', '--32', '-o', str(packing), 'packing.S'], cwd=SOURCE, check=True)
        for section in ('position', 'basis'):
            subprocess.run(['objcopy', '-O', 'binary', '-j', '.' + section, str(packing),
                            str(work / (section + '.bin'))], check=True)
        payload = {'patch.json': SOURCE / 'patch.json',
                   'files/mafia-gpu-clothing.so': library,
                   'files/prepare.py': SOURCE / 'prepare.py',
                   'files/perfmon.py': SOURCE / 'perfmon.py',
                   'files/pack_render.py': SOURCE / 'pack_render.py',
                   'files/position.bin': work / 'position.bin',
                   'files/basis.bin': work / 'basis.bin'}
        pending = work / output.name
        with ZipFile(pending, 'w') as archive:
            for member, path in sorted(payload.items()):
                archive.writestr(ZipInfo(member), path.read_bytes(), compress_type=ZIP_DEFLATED)
        pending.replace(output)


if __name__ == '__main__':
    build(OUTPUT)
    print(OUTPUT.name)
