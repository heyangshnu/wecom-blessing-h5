import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PUBLIC_DIR = ROOT / "public"
PREVIEW_IMAGE = DATA_DIR / "preview-common.jpg"

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080").rstrip("/")
PORT = int(os.getenv("PORT", "8080"))

WECOM_CORP_ID = os.getenv("WECOM_CORP_ID", "")
WECOM_AGENT_ID = os.getenv("WECOM_AGENT_ID", "")
WECOM_SECRET = os.getenv("WECOM_SECRET", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-in-production")

DEV_BYPASS = os.getenv("DEV_BYPASS", "false").lower() in {"1", "true", "yes"}
DEV_USERID = os.getenv("DEV_USERID", "zhangsan")
DEV_NAME = os.getenv("DEV_NAME", "张三")

CARD_TITLE = "你好，初次见面请多多指教"
CARD_DESCRIPTION = "点击开启你的专属祝福"
BLESSING_PATH = "/bless"

WORK_BLESSINGS = [
    "{name}，愿你工作顺利，思路清晰，每天都收获满满成就感。",
    "{name}，愿你在工作中得心应手，所求皆如愿，所行皆坦途。",
    "{name}，愿你职场顺遂，灵感不断，把每一件小事都做得漂亮。",
    "{name}，愿你工作轻松高效，同事合拍，越忙越从容。",
]

HEALTH_BLESSINGS = [
    "{name}，愿你身体健康，作息规律，每天都元气满满。",
    "{name}，愿你身心舒展，少熬夜多运动，活力常伴左右。",
    "{name}，愿你照顾好自己，吃好睡香，笑容比阳光还灿烂。",
    "{name}，愿你平安喜乐，身体棒棒的，才有力气奔赴热爱。",
]
