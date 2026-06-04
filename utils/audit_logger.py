import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)
AUDIT_FILE = LOG_PATH / "ujima_audit.log"

logger = logging.getLogger("ujima_audit")
logger.setLevel(logging.INFO)
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(stream_handler)


def log_event(event: str, details: Dict[str, Any] | None = None) -> None:
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "details": details or {},
    }
    logger.info(json.dumps(payload, ensure_ascii=False))
    with AUDIT_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
