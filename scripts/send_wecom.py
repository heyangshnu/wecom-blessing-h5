#!/usr/bin/env python3
"""从企微自动同步可见成员并发送统一链接的图文卡片。"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server.config import BASE_URL, BLESSING_PATH, CARD_DESCRIPTION, CARD_TITLE
from server.wecom import get_access_token, list_visible_users

load_dotenv(ROOT / ".env")

CORP_ID = os.getenv("WECOM_CORP_ID", "")
AGENT_ID = os.getenv("WECOM_AGENT_ID", "")
SECRET = os.getenv("WECOM_SECRET", "")

PAGE_URL = f"{BASE_URL}{BLESSING_PATH}"
PREVIEW_URL = f"{BASE_URL}/preview/common.jpg"


def send_news(client: httpx.Client, access_token: str, userid: str) -> dict:
    payload = {
        "touser": userid,
        "msgtype": "news",
        "agentid": int(AGENT_ID),
        "news": {
            "articles": [
                {
                    "title": CARD_TITLE,
                    "description": CARD_DESCRIPTION,
                    "url": PAGE_URL,
                    "picurl": PREVIEW_URL,
                }
            ]
        },
        "enable_duplicate_check": 1,
        "duplicate_check_interval": 1800,
    }
    resp = client.post(
        f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}",
        json=payload,
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="从企微同步成员并群发祝福卡片")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不实际发送")
    parser.add_argument("--sync-only", action="store_true", help="只同步成员，不发送")
    parser.add_argument("--limit", type=int, default=0, help="仅处理前 N 人（测试用）")
    args = parser.parse_args()

    if not all([CORP_ID, AGENT_ID, SECRET]):
        raise SystemExit("请在 .env 中配置 WECOM_CORP_ID / WECOM_AGENT_ID / WECOM_SECRET")

    with httpx.Client(timeout=30) as client:
        users = list_visible_users(client)

    if args.limit:
        users = users[: args.limit]

    print(f"已从企微同步 {len(users)} 人（应用可见范围，根部门递归）")
    print(f"统一链接: {PAGE_URL}")
    print(f"封面图: {PREVIEW_URL}")

    for user in users[:5]:
        print(f"  - {user['name']} ({user['userid']}) · {user['department']}")
    if len(users) > 5:
        print(f"  ... 其余 {len(users) - 5} 人")

    if args.sync_only or args.dry_run:
        if args.dry_run:
            print("\n[DRY-RUN] 将发送给以上成员")
        return

    with httpx.Client(timeout=30) as client:
        access_token = get_access_token(client)
        ok, fail = 0, 0

        for user in users:
            result = send_news(client, access_token, user["userid"])
            if result.get("errcode") == 0:
                ok += 1
                print(f"✓ {user['name']} ({user['userid']})")
            else:
                fail += 1
                print(f"✗ {user['name']} ({user['userid']}): {result}")
            time.sleep(0.15)

        print(f"\n完成: 成功 {ok}, 失败 {fail}")


if __name__ == "__main__":
    main()
