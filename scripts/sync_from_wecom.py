#!/usr/bin/env python3
"""预览从企微同步到的成员名单。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server.wecom import list_visible_users

load_dotenv(ROOT / ".env")


def main() -> None:
    if not all(
        [
            os.getenv("WECOM_CORP_ID"),
            os.getenv("WECOM_AGENT_ID"),
            os.getenv("WECOM_SECRET"),
        ]
    ):
        raise SystemExit("请在 .env 中配置 WECOM_CORP_ID / WECOM_AGENT_ID / WECOM_SECRET")

    with httpx.Client(timeout=30) as client:
        users = list_visible_users(client)

    print(f"共 {len(users)} 人：")
    for user in users:
        print(f"- {user['name']} ({user['userid']}) · {user['department']}")


if __name__ == "__main__":
    main()
