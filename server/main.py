import random

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse

from server.config import (
    BASE_URL,
    BLESSING_PATH,
    CARD_DESCRIPTION,
    CARD_TITLE,
    HEALTH_BLESSINGS,
    LIFE_BLESSINGS,
    PREVIEW_IMAGE,
    PUBLIC_DIR,
    WORK_BLESSINGS,
)
from server.preview import generate_common_preview

app = FastAPI(title="WeCom Blessing H5")

NO_CACHE = {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}

CATEGORY_META = {
    "work": {"label": "工作祝福", "icon": "✨", "templates": WORK_BLESSINGS},
    "health": {"label": "健康祝福", "icon": "🌈", "templates": HEALTH_BLESSINGS},
    "life": {"label": "生活祝福", "icon": "🌸", "templates": LIFE_BLESSINGS},
}


def build_random_blessing() -> dict:
    category = random.choice(list(CATEGORY_META.keys()))
    meta = CATEGORY_META[category]
    return {
        "greeting": "送你一句小小祝福",
        "intro": "愿这份随机好运，刚好落在今天",
        "category": category,
        "label": meta["label"],
        "icon": meta["icon"],
        "content": random.choice(meta["templates"]),
    }


@app.get("/api/blessing/random")
def blessing_random():
    return build_random_blessing()


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
def blessing_page():
    return FileResponse(PUBLIC_DIR / "index.html", headers=NO_CACHE)


@app.get("/js/app.js")
def app_js():
    return FileResponse(PUBLIC_DIR / "js" / "app.js", media_type="application/javascript", headers=NO_CACHE)


@app.get("/css/style.css")
def app_css():
    return FileResponse(PUBLIC_DIR / "css" / "style.css", media_type="text/css", headers=NO_CACHE)


@app.get("/images/{filename}")
def static_image(filename: str):
    path = PUBLIC_DIR / "images" / filename
    if not path.is_file():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")
    media = "image/gif" if filename.endswith(".gif") else "image/png" if filename.endswith(".png") else "image/jpeg"
    return FileResponse(path, media_type=media, headers=NO_CACHE)


@app.get("/videos/{filename}")
def static_video(filename: str):
    path = PUBLIC_DIR / "videos" / filename
    if not path.is_file():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")
    media = "video/webm" if filename.endswith(".webm") else "video/mp4" if filename.endswith(".mp4") else "application/octet-stream"
    return FileResponse(path, media_type=media, headers=NO_CACHE)


@app.get("/")
def root_redirect():
    return RedirectResponse(BLESSING_PATH)
