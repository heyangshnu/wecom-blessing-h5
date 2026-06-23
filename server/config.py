import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
PUBLIC_DIR = ROOT / "public"
PREVIEW_IMAGE = DATA_DIR / "preview-common.jpg"

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080").rstrip("/")
PORT = int(os.getenv("PORT", "8080"))

WECOM_CORP_ID = os.getenv("WECOM_CORP_ID", "")
WECOM_AGENT_ID = os.getenv("WECOM_AGENT_ID", "")
WECOM_SECRET = os.getenv("WECOM_SECRET", "")

CARD_TITLE = "你好，初次见面请多多指教"
CARD_DESCRIPTION = "点击开启你的随机祝福"
BLESSING_PATH = "/bless"

WORK_BLESSINGS = [
    "愿你工作顺利，思路清晰，每天都收获满满成就感。",
    "愿你在工作中得心应手，所求皆如愿，所行皆坦途。",
    "愿你职场顺遂，灵感不断，把每一件小事都做得漂亮。",
    "愿你工作轻松高效，同事合拍，越忙越从容。",
    "愿你今日事今日毕，少加班多收获，下班路上都是好风景。",
]

HEALTH_BLESSINGS = [
    "愿你身体健康，作息规律，每天都元气满满。",
    "愿你身心舒展，少熬夜多运动，活力常伴左右。",
    "愿你照顾好自己，吃好睡香，笑容比阳光还灿烂。",
    "愿你平安喜乐，身体棒棒的，才有力气奔赴热爱。",
    "愿你春有百花秋有月，身强体健，万事胜意。",
]

LIFE_BLESSINGS = [
    "愿你被温柔以待，所遇皆美好，所念皆如愿。",
    "愿你眼里有光，心中有爱，脚下有路，前方有惊喜。",
    "愿你忙时不乱，闲时不慌，把平凡日子过成诗。",
    "愿你与美好不期而遇，与幸运撞个满怀。",
    "愿你保持热爱，奔赴下一场山海。",
]
