#!/usr/bin/env python3
"""从 CSV 导入名单，生成 token 并写入 data/users.json。"""

from __future__ import annotations

import argparse
import csv
import json
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USERS_FILE = ROOT / "data" / "users.json"


def make_token(existing: set[str]) -> str:
    while True:
        token = secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:10]
        if token not in existing:
            return token


def load_csv(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            userid = (row.get("userid") or "").strip()
            if not name or not userid:
                continue
            rows.append(
                {
                    "name": name,
                    "userid": userid,
                    "department": (row.get("department") or "").strip(),
                    "work_blessing": (row.get("work_blessing") or "").strip(),
                    "health_blessing": (row.get("health_blessing") or "").strip(),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="初始化祝福名单")
    parser.add_argument("csv", type=Path, help="名单 CSV 路径")
    parser.add_argument(
        "--merge",
        action="store_true",
        help="保留已有 token，仅更新/追加 CSV 中的人",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        raise SystemExit(f"找不到 CSV: {args.csv}")

    existing: dict = {}
    if args.merge and USERS_FILE.exists():
        existing = json.loads(USERS_FILE.read_text(encoding="utf-8"))

    used_tokens = set(existing.keys())
    userid_to_token = {v["userid"]: k for k, v in existing.items()}

    rows = load_csv(args.csv)
    output: dict = dict(existing)

    for row in rows:
        token = userid_to_token.get(row["userid"]) or make_token(used_tokens)
        used_tokens.add(token)
        output[token] = row

    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已写入 {len(output)} 人 -> {USERS_FILE}")
    print("\n示例链接（请替换 BASE_URL）：")
    for token, user in list(output.items())[:3]:
        print(f"  {user['name']} ({user['userid']}): /g/{token}")


if __name__ == "__main__":
    main()
