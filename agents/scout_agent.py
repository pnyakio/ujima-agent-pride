from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from config.guardrails import communication_limit, dignity_filter
from memory.trail_memory import TrailMemory
from utils.fallback_manager import FallbackManager


@dataclass
class ScoutOutput:
    stress_detected: bool
    stress_reason: str
    next_harvest: str
    savings: float
    literacy_message: str
    notify_guardian: bool
    sms_status: str


class ScoutAgent:
    def __init__(self) -> None:
        self.memory = TrailMemory(region="africa")
        self.fallback = FallbackManager()
        self.sms_sent_today = 0

    def observe(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        purpose = applicant.get("purpose", "").lower()
        stress_reason = "none"
        stress_detected = False

        if "loan shark" in purpose:
            stress_detected = True
            stress_reason = "loan_shark"
        elif "school fees" in purpose:
            stress_detected = True
            stress_reason = "school_fees"
        elif "financial stress" in purpose or "debt collector" in purpose:
            stress_detected = True
            stress_reason = "financial_stress"
        elif applicant.get("savings", 0) < applicant.get("loan_amount", 0) * 0.35:
            stress_detected = True
            stress_reason = "low_savings"

        notify_guardian = stress_detected or "loan shark" in purpose or "school fees" in purpose
        next_harvest = self._estimate_next_harvest()
        literacy_message = self._generate_literacy_message(applicant, stress_detected)
        sms_status = "within limit" if communication_limit(self.sms_sent_today) else "daily limit reached"
        if communication_limit(self.sms_sent_today):
            self.sms_sent_today += 1

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "applicant": applicant.get("name"),
            "purpose": applicant.get("purpose"),
            "stress_detected": stress_detected,
            "stress_reason": stress_reason,
            "next_harvest": next_harvest,
            "savings": applicant.get("savings", 0),
            "notify_guardian": notify_guardian,
            "sms_status": sms_status,
        }
        self.memory.store(record)

        return {
            "stress_detected": stress_detected,
            "stress_reason": stress_reason,
            "next_harvest": next_harvest,
            "savings": applicant.get("savings", 0),
            "literacy_message": dignity_filter(literacy_message),
            "notify_guardian": notify_guardian,
            "sms_status": sms_status,
        }

    def _estimate_next_harvest(self) -> str:
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
        next_month_index = (datetime.utcnow().month + 2) % 12
        return month_names[next_month_index]

    def _generate_literacy_message(self, applicant: Dict[str, Any], stress_detected: bool) -> str:
        coaching_prompt = (
            f"You are a financial literacy coach for informal traders in Kenya. "
            f"The applicant is a {applicant.get('occupation')} from {applicant.get('county')} with "
            f"KES {applicant.get('income')} monthly income and KES {applicant.get('savings')} savings. "
            f"They are requesting KES {applicant.get('loan_amount')} for '{applicant.get('purpose')}'. "
            f"Generate an empathetic, respectful coaching message without recommending a loan. "
            f"If financial stress is detected, mention harvest planning and school fee timing."
        )
        result = self.fallback.complete(coaching_prompt)
        return result.text if result.success else (
            "Additional financial history is needed before the next credit conversation. "
            "Support the applicant with harvest planning and saving strategies."
        )
