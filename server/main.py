import random
import secrets

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from server.config import (
    BASE_URL,
    BLESSING_PATH,
    CARD_DESCRIPTION,
    CARD_TITLE,
    DEV_BYPASS,
    DEV_NAME,
    DEV_USERID,
    HEALTH_BLESSINGS,
    PREVIEW_IMAGE,
    PUBLIC_DIR,
    SESSION_SECRET,
    WECOM_AGENT_ID,
    WECOM_CORP_ID,
    WECOM_SECRET,
    WORK_BLESSINGS,
)
from server.preview import generate_common_preview
from server.wecom import build_oauth_url, get_user_profile, get_userid_from_code

app = FastAPI(title="WeCom Blessing H5")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax")

NO_CACHE = {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}

CATEGORY_META = {
    "work": {"label": "工作祝福", "icon": "✨"},
    "health": {"label": "健康祝福", "icon": "🌈"},
}


def wecom_configured() -> bool:
    return bool(WECOM_CORP_ID and WECOM_AGENT_ID and WECOM_SECRET)


def build_blessing(profile: dict[str, str]) -> dict:
    name = profile["name"]
    category = random.choice(["work", "health"])
    templates = WORK_BLESSINGS if category == "work" else HEALTH_BLESSINGS
    meta = CATEGORY_META[category]
    return {
        "greeting": "很高兴认识你",
        "intro": "送你一句小小祝福",
        "category": category,
        "label": meta["label"],
        "icon": meta["icon"],
        "content": random.choice(templates).format(name=name),
    }


def get_session_profile(request: Request) -> dict[str, str] | None:
    userid = request.session.get("userid")
    name = request.session.get("name")
    if not userid or not name:
        return None
    return {"userid": userid, "name": name}


def set_session_profile(request: Request, profile: dict[str, str]) -> None:
    request.session["userid"] = profile["userid"]
    request.session["name"] = profile["name"]


@app.get("/api/blessing/me")
def blessing_me(request: Request):
    profile = get_session_profile(request)
    if not profile:
        raise HTTPException(status_code=401, detail="未登录，请在企业微信中打开链接")
    return build_blessing(profile)


@app.get("/api/card-meta")
def card_meta():
    preview_url = f"{BASE_URL}/preview/common.jpg"
    return {
        "title": CARD_TITLE,
        "description": CARD_DESCRIPTION,
        "picurl": preview_url,
        "url": f"{BASE_URL}{BLESSING_PATH}",
    }


@app.get("/preview/common.jpg")
def common_preview():
    if not PREVIEW_IMAGE.exists():
        generate_common_preview(PREVIEW_IMAGE)
    return FileResponse(PREVIEW_IMAGE, media_type="image/jpeg")


@app.get(BLESSING_PATH)
def blessing_entry(request: Request, dev_userid: str | None = None):
    profile = get_session_profile(request)
    if profile:
        return FileResponse(PUBLIC_DIR / "index.html", headers=NO_CACHE)

    if DEV_BYPASS:
        userid = dev_userid or DEV_USERID
        if dev_userid:
            try:
                with httpx.Client(timeout=20) as client:
                    profile = get_user_profile(client, userid)
            except Exception:
                profile = {"userid": userid, "name": DEV_NAME}
        else:
            profile = {"userid": DEV_USERID, "name": DEV_NAME}
        set_session_profile(request, profile)
        return FileResponse(PUBLIC_DIR / "index.html", headers=NO_CACHE)

    if not wecom_configured():
        raise HTTPException(status_code=500, detail="未配置企微应用，请检查 .env")

    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state
    redirect_uri = f"{BASE_URL}/oauth/callback"
    return RedirectResponse(build_oauth_url(redirect_uri, state))


@app.get("/oauth/callback")
def oauth_callback(request: Request, code: str | None = None, state: str | None = None):
    saved_state = request.session.pop("oauth_state", None)
    if not code or not state or state != saved_state:
        raise HTTPException(status_code=400, detail="OAuth 校验失败，请重新打开链接")

    try:
        with httpx.Client(timeout=20) as client:
            userid = get_userid_from_code(client, code)
            profile = get_user_profile(client, userid)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    set_session_profile(request, profile)
    return RedirectResponse(BLESSING_PATH)


@app.get("/js/app.js")
def app_js():
    return FileResponse(PUBLIC_DIR / "js" / "app.js", media_type="application/javascript", headers=NO_CACHE)


@app.get("/css/style.css")
def app_css():
    return FileResponse(PUBLIC_DIR / "css" / "style.css", media_type="text/css", headers=NO_CACHE)


@app.get("/")
def root_redirect():
    return RedirectResponse(BLESSING_PATH)

