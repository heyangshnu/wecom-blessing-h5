#!/usr/bin/env python3
"""生成企微卡片通用封面图。"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server.preview import generate_common_preview

if __name__ == "__main__":
    out = ROOT / "data" / "preview-common.jpg"
    generate_common_preview(out)
    print(f"已生成: {out}")
