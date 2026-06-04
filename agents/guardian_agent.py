from dataclasses import dataclass
from typing import Any, Dict, List

from config.guardrails import check_gender_proxy, dignity_filter, unusual_pattern_alert
from utils.bias_checker import BiasChecker


@dataclass
class GuardianOutput:
    risk_score: int
    risk_flags: List[str]
    decision: str
    track_results: Dict[str, Any]
    safety_alerts: List[str]
    decision_message: str


class GuardianAgent:
    def __init__(self) -> None:
        self.bias_checker = BiasChecker()

    def guard(self, applicant: Dict[str, Any], scout_output: Dict[str, Any]) -> Dict[str, Any]:
        purpose = applicant.get("purpose", "").lower()
        risk_flags: List[str] = []
        safety_alerts: List[str] = []

        if applicant.get("loan_amount", 0) > 15000:
            risk_flags.append("high_loan_amount")
        if applicant.get("children_under_5", 0) >= 2:
            risk_flags.append("multiple_young_children")
        if "debt collector" in purpose:
            risk_flags.append("debt_collector_mention")
        if scout_output.get("stress_detected"):
            risk_flags.append("stress_signal")
        if applicant.get("savings", 0) < applicant.get("loan_amount", 0) * 0.3:
            risk_flags.append("savings_gap")

        risk_score = self._estimate_risk_score(applicant, scout_output)
        track_results = self.bias_checker.run_track_audit(applicant, risk_score)

        if len(risk_flags) >= 3:
            decision = "deny_recommendation"
        elif applicant.get("loan_amount", 0) > 15000 or risk_score >= 70 or scout_output.get("stress_detected"):
            decision = "escalate"
        else:
            decision = "human_review_required"

        gender_proxies = check_gender_proxy(applicant)
        if gender_proxies:
            safety_alerts.append("gender_proxy_policy_violation")

        if unusual_pattern_alert(
            track_results.get("representation", {}).get("county_rate", 0.0),
            track_results.get("representation", {}).get("baseline_rate", 1.0),
        ):
            safety_alerts.append("subcounty_approval_rate_drop")

        decision_message = dignity_filter(
            "Additional financial history is needed before approval. "
            "Please review the applicant’s full repayment capacity and cultural context."
        )

        return {
            "risk_score": risk_score,
            "risk_flags": risk_flags,
            "decision": decision,
            "track_results": track_results,
            "safety_alerts": safety_alerts,
            "decision_message": decision_message,
        }

    def _estimate_risk_score(self, applicant: Dict[str, Any], scout_output: Dict[str, Any]) -> int:
        score = 40
        loan_amount = applicant.get("loan_amount", 0)
        income = applicant.get("income", 0)
        savings = applicant.get("savings", 0)
        children = applicant.get("children_under_5", 0)
        purpose = applicant.get("purpose", "").lower()

        if loan_amount > 15000:
            score += 18
        if income < 15000:
            score += 15
        if savings < 5000:
            score += 12
        score += min(children * 5, 20)
        if "debt collector" in purpose:
            score += 15
        if scout_output.get("stress_detected"):
            score += 10

        if income > 30000 and savings > 15000:
            score -= 10

        return max(min(score, 100), 0)
