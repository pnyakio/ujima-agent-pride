from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class TrailMemory:
    def __init__(self, region: str = "africa") -> None:
        self.records: List[Dict[str, Any]] = []
        self.region = region
        self.storage_path = Path("logs")
        self.storage_path.mkdir(exist_ok=True)

    def store(self, event: Dict[str, Any]) -> None:
        event_copy = dict(event)
        event_copy["region"] = self.region
        event_copy["stored_at"] = datetime.utcnow().isoformat() + "Z"
        self.records.append(event_copy)

    def retrieve(self) -> List[Dict[str, Any]]:
        return list(self.records)
