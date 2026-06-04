from datetime import datetime
from typing import Any, Dict

try:
    import crewai
except ImportError:  # pragma: no cover
    crewai = None

from agents.guardian_agent import GuardianAgent
from agents.hunter_agent import HunterAgent
from agents.scout_agent import ScoutAgent
from memory.trail_memory import TrailMemory
from tasks.guardian_task import GuardianTask
from tasks.hunter_task import HunterTask
from tasks.scout_task import ScoutTask
from utils.audit_logger import log_event


class UjimaCrew:
    def __init__(self) -> None:
        self.scout = ScoutAgent()
        self.guardian = GuardianAgent()
        self.hunter = HunterAgent()
        self.scout_task = ScoutTask(self.scout)
        self.guardian_task = GuardianTask(self.guardian)
        self.hunter_task = HunterTask(self.hunter)
        self.memory = TrailMemory(region="africa")
        self.active_provider = "None"
        self.crewai_enabled = crewai is not None

    def prepare(self) -> None:
        if self.crewai_enabled:
            log_event("crew_prepare", {"status": "ready", "framework": "crewai"})
        else:
            log_event("crew_prepare", {"status": "ready", "framework": "internal"})

    def execute_pipeline(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        scout_output = self.scout_task.run(applicant)
        guardian_output = self.guardian_task.run(applicant, scout_output)
        hunter_output = self.hunter_task.run(applicant, guardian_output)

        self.active_provider = self.scout.fallback.active_provider or "Cerebras"

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "applicant": applicant.get("name"),
            "county": applicant.get("county"),
            "loan_amount": applicant.get("loan_amount"),
            "provider": self.active_provider,
            "scout": scout_output,
            "guardian": guardian_output,
            "hunter": hunter_output,
        }
        self.memory.store(record)
        log_event("pipeline_executed", {"applicant": applicant.get("name"), "provider": self.active_provider})

        return {
            "scout": scout_output,
            "guardian": guardian_output,
            "hunter": hunter_output,
            "provider": self.active_provider,
        }
