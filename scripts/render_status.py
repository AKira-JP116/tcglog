from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "site-status.json"


def main() -> None:
    now = datetime.now().astimezone()
    payload = {
        "lastPublishedAt": now.isoformat(),
        "schedule": ["09:00", "15:00", "21:00"],
        "timezone": "Asia/Tokyo",
    }
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {DATA}")


if __name__ == "__main__":
    main()
