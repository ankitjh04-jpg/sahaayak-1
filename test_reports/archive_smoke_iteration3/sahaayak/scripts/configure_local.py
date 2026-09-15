"""Create local environment files without overwriting existing configuration."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

def configure():
    for folder in (ROOT, ROOT / 'backend', ROOT / 'frontend'):
        destination = folder / '.env'
        if destination.exists():
            print(f'Preserved: {destination.relative_to(ROOT)}')
        else:
            shutil.copyfile(folder / '.env.example', destination)
            print(f'Created: {destination.relative_to(ROOT)}')
    print('Add Twilio/Google/OpenWeather credentials privately in backend/.env when ready.')

if __name__ == '__main__':
    configure()