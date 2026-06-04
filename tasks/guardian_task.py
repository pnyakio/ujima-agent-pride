from agents.guardian_agent import GuardianAgent
from typing import Any, Dict


class GuardianTask:
    def __init__(self, agent: GuardianAgent):
        self.agent = agent

    def run(self, applicant: Dict[str, Any], scout_output: Dict[str, Any]) -> Dict[str, Any]:
        return self.agent.guard(applicant, scout_output)
