from __future__ import annotations

import time
from typing import Any
from urllib.parse import quote

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


def build_oauth_url(redirect_uri: str, state: str) -> str:
    encoded = quote(redirect_uri, safe="")
    return (
        f"https://open.weixin.qq.com/connect/oauth2/authorize"
        f"?appid={WECOM_CORP_ID}"
        f"&redirect_uri={encoded}"
        f"&response_type=code"
        f"&scope=snsapi_base"
        f"&agentid={WECOM_AGENT_ID}"
        f"&state={quote(state, safe='')}"
        f"#wechat_redirect"
    )


def get_userid_from_code(client: httpx.Client, code: str) -> str:
    access_token = get_access_token(client)
    resp = client.get(
        "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo",
        params={"access_token": access_token, "code": code},
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode") not in (0, None):
        raise RuntimeError(f"getuserinfo 失败: {data}")
    userid = data.get("UserId") or data.get("userid")
    if not userid:
        raise RuntimeError("未能识别企微成员身份，请在企业微信内打开")
    return userid


def get_department_name(client: httpx.Client, access_token: str, department_id: int) -> str:
    resp = client.get(
        "https://qyapi.weixin.qq.com/cgi-bin/department/get",
        params={"access_token": access_token, "id": department_id},
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode") != 0:
        return "团队"
    return data.get("department", {}).get("name") or "团队"


def get_user_profile(client: httpx.Client, userid: str) -> dict[str, str]:
    access_token = get_access_token(client)
    resp = client.get(
        "https://qyapi.weixin.qq.com/cgi-bin/user/get",
        params={"access_token": access_token, "userid": userid},
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode") != 0:
        raise RuntimeError(f"user/get 失败: {data}")

    name = data.get("name") or userid
    department = "团队"
    dept_ids = data.get("department") or []
    if dept_ids:
        department = get_department_name(client, access_token, int(dept_ids[0]))

    return {
        "userid": userid,
        "name": name,
        "department": department,
    }


def list_visible_users(client: httpx.Client) -> list[dict[str, str]]:
    """从根部门递归拉取应用可见范围内的全部成员，无需手动传部门 ID。"""
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
                "department": _resolve_department_name(client, access_token, item.get("department") or []),
            }
        )
    return users


def _resolve_department_name(
    client: httpx.Client, access_token: str, department_ids: list[int]
) -> str:
    if not department_ids:
        return "团队"
    return get_department_name(client, access_token, int(department_ids[0]))
