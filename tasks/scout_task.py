from agents.scout_agent import ScoutAgent
from typing import Any, Dict


class ScoutTask:
    def __init__(self, agent: ScoutAgent):
        self.agent = agent

    def run(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        return self.agent.observe(applicant)
