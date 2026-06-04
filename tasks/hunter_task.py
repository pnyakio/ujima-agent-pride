from agents.hunter_agent import HunterAgent
from typing import Any, Dict


class HunterTask:
    def __init__(self, agent: HunterAgent):
        self.agent = agent

    def run(self, applicant: Dict[str, Any], guardian_output: Dict[str, Any]) -> Dict[str, Any]:
        return self.agent.hunt(applicant, guardian_output)
