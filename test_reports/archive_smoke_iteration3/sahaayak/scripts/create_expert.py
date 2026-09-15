"""Use the local virtualenv automatically, then run expert provisioning."""
from pathlib import Path
import os
import sys
ROOT = Path(__file__).resolve().parents[1]
if sys.prefix == sys.base_prefix:
    executable = ROOT / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    if executable.exists() and Path(sys.executable).resolve() != executable.resolve():
        os.execv(str(executable), [str(executable), str(Path(__file__).resolve()), *sys.argv[1:]])
sys.path.insert(0, str(ROOT / 'backend'))
from app.manage import main
if __name__ == '__main__': main()