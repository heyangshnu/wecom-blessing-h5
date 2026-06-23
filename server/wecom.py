from __future__ import annotations

import time
from typing import Any

import httpx

from server.config import WECOM_AGENT_ID, WECOM_CORP_ID, WECOM_SECRET

_token_cache: dict[str, Any] = {"value": "", "expires_at": 0.0}


def get_access_token(client: httpx.Client | None = None) -> str:
    now = time.time()
    if _token_cache["value"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["value"]

    owns_client = client is None
    if owns_client:
        client = httpx.Client(timeout=20)

    try:
        resp = client.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
            params={"corpid": WECOM_CORP_ID, "corpsecret": WECOM_SECRET},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode") != 0:
            raise RuntimeError(f"gettoken 失败: {data}")

        _token_cache["value"] = data["access_token"]
        _token_cache["expires_at"] = now + int(data.get("expires_in", 7200))
        return _token_cache["value"]
    finally:
        if owns_client:
            client.close()


def list_visible_users(client: httpx.Client) -> list[dict[str, str]]:
    """从根部门递归拉取应用可见范围内的全部成员。"""
    access_token = get_access_token(client)
    resp = client.get(
        "https://qyapi.weixin.qq.com/cgi-bin/user/list",
        params={
            "access_token": access_token,
            "department_id": 1,
            "fetch_child": 1,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode") != 0:
        raise RuntimeError(f"user/list 失败: {data}")

    seen: set[str] = set()
    users: list[dict[str, str]] = []
    for item in data.get("userlist", []):
        userid = item.get("userid")
        if not userid or userid in seen:
            continue
        seen.add(userid)
        users.append(
            {
                "userid": userid,
                "name": item.get("name") or userid,
            }
        )
    return users
