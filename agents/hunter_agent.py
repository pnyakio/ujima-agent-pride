from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class HunterOutput:
    applicant: str
    occupation: str
    county: str
    request: float
    risk_score: int
    recommendation: str
    briefing: str


class HunterAgent:
    def __init__(self) -> None:
        pass

    def hunt(self, applicant: Dict[str, Any], guardian_output: Dict[str, Any]) -> Dict[str, Any]:
        decision = guardian_output.get("decision", "human_review_required")
        recommendation = "Human review required."
        if decision == "deny_recommendation":
            recommendation = "Recommend additional verification and supportive guidance before final action."
        elif decision == "escalate":
            recommendation = "Escalate to the officer team within 15 minutes for human-led assessment."

        briefing = (
            f"Applicant: {applicant.get('name')}\n"
            f"Occupation: {applicant.get('occupation')}\n"
            f"County: {applicant.get('county')}\n"
            f"Request: {applicant.get('loan_amount')} KES\n"
            f"Risk Score: {guardian_output.get('risk_score')}\n"
            f"Recommendation: {recommendation}"
        )

        return {
            "applicant": applicant.get("name"),
            "occupation": applicant.get("occupation"),
            "county": applicant.get("county"),
            "request": applicant.get("loan_amount"),
            "risk_score": guardian_output.get("risk_score"),
            "recommendation": recommendation,
            "briefing": briefing,
        }
