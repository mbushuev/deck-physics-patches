"""Generate the installer catalog from the published per-game patch archives."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


def catalog():
    games = {}
    identifiers = set()
    for path in sorted((ROOT / 'patches').glob('*/*.deckphysx.zip')):
        with ZipFile(path) as zip_file:
            if zip_file.testzip() is not None:
                raise ValueError(f'Damaged patch archive: {path.name}')
            patch = json.loads(zip_file.read('patch.json'))
        key = patch['app_id'], patch['id']
        if key in identifiers:
            raise ValueError(f'Duplicate patch: {key}')
        identifiers.add(key)
        data = path.read_bytes()
        games.setdefault(key[0], []).append({
            'path': path.relative_to(ROOT).as_posix(),
            'size': len(data),
            'sha256': sha256(data).hexdigest(),
        })
    return json.dumps({'format': 1, 'games': games}, indent=2, sort_keys=True) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify the committed catalog')
    options = parser.parse_args()
    output = ROOT / 'catalog.json'
    expected = catalog()
    if options.check:
        if output.read_text(encoding='utf-8') != expected:
            parser.exit(1, 'Patch catalog is stale. Rebuild it with tools/Build-PatchCatalog.py.\n')
    else:
        output.write_text(expected, encoding='utf-8', newline='\n')
