"""Build a source-only download. Runtime files, credentials and databases excluded."""
from pathlib import Path
import hashlib
import json
import zipfile
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'frontend' / 'public' / 'downloads'
EXCLUDED = {'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache', 'private_objects', 'build', 'dist', 'downloads', '.git', 'test_reports', 'memory', '.cache'}
ROOT_FILES = {'README.md', 'docker-compose.yml', '.env.example', '.gitignore'}

def source_files():
    for file in ROOT.rglob('*'):
        if not file.is_file() or file.is_symlink(): continue
        relative = file.relative_to(ROOT)
        if relative.parts[0] not in {'frontend', 'backend', 'docs', 'scripts'} and str(relative) not in ROOT_FILES: continue
        if any(part in EXCLUDED or part.endswith('.egg-info') for part in relative.parts): continue
        if file.name.startswith('.env') and file.name != '.env.example': continue
        if file.suffix in {'.pyc', '.log', '.zip', '.db', '.sqlite'}: continue
        if file.name in {'test_credentials.md', '.DS_Store'}: continue
        yield file, relative

def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    archive = OUTPUT / 'sahaayak-local.zip'
    manifest = []
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for file, relative in sorted(source_files()):
            bundle.write(file, Path('sahaayak') / relative)
            manifest.append(str(relative))
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (OUTPUT / 'README.md').write_bytes((ROOT / 'README.md').read_bytes())
    (OUTPUT / 'SHA256SUMS.txt').write_text(f'{checksum}  sahaayak-local.zip\n')
    (OUTPUT / 'manifest.json').write_text(json.dumps({'archive': archive.name, 'sha256': checksum, 'files': manifest, 'contains_credentials': False, 'contains_runtime_database': False}, indent=2))
    print(f'Created {archive.name}: {len(manifest)} source files, {archive.stat().st_size} bytes; secrets/configuration and runtime uploads excluded.')

if __name__ == '__main__': build()