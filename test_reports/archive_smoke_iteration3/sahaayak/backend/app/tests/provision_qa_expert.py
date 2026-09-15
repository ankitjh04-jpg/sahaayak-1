import asyncio
import json
import secrets
from datetime import datetime

from app.manage import create


async def main():
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    email = f"qa.expert.{stamp}.{secrets.randbelow(9999)}@example.com"
    password = f"QaExpert!{secrets.token_hex(6)}"
    name = f"QA Expert {stamp[-6:]}"
    await create(email=email, name=name, password=password, reset=False)
    path = "/app/test_reports/qa_expert_credentials.json"
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"email": email, "password": password, "name": name}, handle)
    print(path)


if __name__ == "__main__":
    asyncio.run(main())
