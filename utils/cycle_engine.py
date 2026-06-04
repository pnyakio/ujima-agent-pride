from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CycleEngine:
    total_applications: int = 0
    escalations: int = 0
    repaid_count: int = 0
    csat_scores: List[int] = field(default_factory=list)
    validation_status: str = "Pending Approval"

    def record_application(self, guardian_output: Dict[str, Any], applicant: Dict[str, Any]) -> None:
        self.total_applications += 1
        if guardian_output.get("decision") == "escalate":
            self.escalations += 1
        if guardian_output.get("risk_score", 0) < 70:
            self.repaid_count += 1
        self.csat_scores.append(4)

    def average_csat(self) -> float:
        if not self.csat_scores:
            return 0.0
        return sum(self.csat_scores) / len(self.csat_scores)

    def repayment_rate(self) -> float:
        if self.total_applications == 0:
            return 0.0
        return float(self.repaid_count) / self.total_applications

    def escalation_rate(self) -> float:
        if self.total_applications == 0:
            return 0.0
        return float(self.escalations) / self.total_applications

    def generate_insights(self) -> Dict[str, str]:
        insights = (
            f"{int(self.escalation_rate() * 100)}% of applications are escalated for human review. "
            f"Projected repayment rate is {int(self.repayment_rate() * 100)}% with current policy enforcement."
        )

        recommendation = (
            "Integrate Ministry of Education term calendar, strengthen harvest cycle coaching, "
            "and maintain review packets for high-risk borrowers."
        )

        return {
            "insights": insights,
            "recommendation": recommendation,
        }

    def set_validation_status(self, status: str) -> None:
        if status in {"Pending Approval", "Approved", "Rejected"}:
            self.validation_status = status
