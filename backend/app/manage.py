"""Local-admin expert provisioning. No public expert registration endpoint."""
import argparse
import asyncio
import getpass
import re
from .db import db, create_indexes, client
from .security.auth import uid, stamp, audit
from .security.passwords import hash_password

async def create(email, name, password, reset=False):
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or len(email) > 254:
        raise ValueError('Enter a valid email')
    if not 2 <= len(name) <= 80 or not 12 <= len(password) <= 256:
        raise ValueError('Name must be 2-80 characters and password 12-256 characters')
    await create_indexes()
    existing = await db.users.find_one({'email': email}, {'_id': 0})
    if existing and (not reset or existing['role'] != 'expert'):
        raise ValueError('Account exists. Use --reset-password for an existing expert.')
    identifier = existing['id'] if existing else uid()
    await db.users.update_one({'id': identifier}, {'$set': {'email': email, 'role': 'expert', 'password_hash': hash_password(password), 'disabled': False, 'language': 'en', 'profile': {'name': name, 'location': '', 'name_source': 'administrator'}, 'updated_at': stamp()}, '$setOnInsert': {'id': identifier, 'created_at': stamp()}}, upsert=True)
    await db.sessions.delete_many({'user_id': identifier})
    await audit('local-administrator', 'expert.account_configured', identifier)
    return identifier

def main():
    parser = argparse.ArgumentParser(description='Create an approved agricultural expert')
    parser.add_argument('--email')
    parser.add_argument('--name')
    parser.add_argument('--reset-password', action='store_true')
    args = parser.parse_args()
    email = (args.email or input('Expert email: ')).strip().lower()
    name = (args.name or input('Expert full name: ')).strip()
    password = getpass.getpass('Password (12+ characters; hidden): ')
    if password != getpass.getpass('Confirm password: '):
        raise SystemExit('Passwords do not match.')
    try:
        asyncio.run(create(email, name, password, args.reset_password))
        print('Expert account configured. Sign in at /expert/login. Password was not printed or saved to a file.')
    except Exception:
        raise SystemExit('Could not configure account. Check MongoDB, email uniqueness, name length (2-80) and password length (12-256).') from None
    finally:
        client.close()

if __name__ == '__main__': main()