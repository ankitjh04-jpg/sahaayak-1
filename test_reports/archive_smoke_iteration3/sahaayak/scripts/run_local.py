"""Run both development servers; never silently chooses different ports."""
from pathlib import Path
import os
import shutil
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def env_file(path):
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            result[key] = value.strip().strip('"').strip("'")
    return result

def main():
    python = ROOT / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    yarn = shutil.which('yarn.cmd' if sys.platform == 'win32' else 'yarn')
    if not python.exists() or not yarn:
        raise SystemExit('Run python scripts/setup_local.py first.')
    backend = env_file(ROOT / 'backend' / '.env')
    frontend = env_file(ROOT / 'frontend' / '.env')
    for port in (int(backend['BACKEND_PORT']), int(frontend['PORT'])):
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1', port)) == 0:
                raise SystemExit(f'Port {port} is already in use. Stop that process first.')
    children = []
    try:
        kwargs = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == 'win32' else {'start_new_session': True}
        children.append(subprocess.Popen([str(python), '-m', 'uvicorn', 'app.main:app', '--host', backend['BACKEND_HOST'], '--port', backend['BACKEND_PORT'], '--reload'], cwd=ROOT / 'backend', **kwargs))
        children.append(subprocess.Popen([yarn, 'start'], cwd=ROOT / 'frontend', env={**os.environ, 'BROWSER': 'none'}, **kwargs))
        print(f"\nOpen {backend['FRONTEND_ORIGIN']} in your browser. Ctrl+C stops both servers.")
        while all(child.poll() is None for child in children):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for child in children:
            if child.poll() is None:
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], capture_output=True)
                else:
                    os.killpg(child.pid, signal.SIGTERM)

if __name__ == '__main__':
    main()