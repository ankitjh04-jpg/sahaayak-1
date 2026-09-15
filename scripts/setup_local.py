"""VS Code one-time setup. Python 3.11+, Node 20+ and Yarn required."""
from pathlib import Path
import shutil
import subprocess
import sys
import venv
from configure_local import configure

ROOT = Path(__file__).resolve().parents[1]

def find_yarn():
    yarn = shutil.which('yarn.cmd' if sys.platform == 'win32' else 'yarn')
    if yarn:
        return [yarn]
    corepack = shutil.which('corepack.cmd' if sys.platform == 'win32' else 'corepack')
    if corepack:
        return [corepack, 'yarn']
    return None

def main():
    if sys.version_info < (3, 11):
        raise SystemExit('Python 3.11 or newer is required.')
    yarn = find_yarn()
    node = shutil.which('node')
    if not node or not yarn:
        raise SystemExit('Install Node.js 20+ and enable Yarn through Corepack first. See README -> prerequisites.')
    version = subprocess.check_output([node, '--version'], text=True).strip()
    if int(version.lstrip('v').split('.')[0]) < 20:
        raise SystemExit('Node.js 20 or newer is required.')
    configure()
    if not (ROOT / '.venv').exists():
        venv.EnvBuilder(with_pip=True).create(ROOT / '.venv')
    python = ROOT / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    subprocess.run([str(python), '-m', 'pip', 'install', '-e', str(ROOT / 'backend')], check=True)
    subprocess.run([*yarn, 'install', '--frozen-lockfile'], cwd=ROOT / 'frontend', check=True)
    print('\nSetup complete. Start MongoDB, create an expert with python scripts/create_expert.py, then run python scripts/run_local.py')

if __name__ == '__main__':
    main()