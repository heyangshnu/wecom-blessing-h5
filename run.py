#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
import uvicorn

load_dotenv(ROOT / ".env")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("server.main:app", host="0.0.0.0", port=port, reload=True)
