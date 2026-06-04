from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BLOCKED_PROXIES = [
    "female",
    "male",
    "tribe",
    "ethnicity",
]

MAX_SMS_PER_DAY = 3
UNUSUAL_PATTERN_DROP_THRESHOLD = 0.3
LOG_DIRECTORY = Path("logs")
LOG_DIRECTORY.mkdir(exist_ok=True)

DIGNITY_REPLACEMENTS = {
    "risky person": "individual who requires additional review",
    "unreliable": "needs more supportive history",
    "problematic borrower": "someone with gaps in their credit narrative",
}


def dignity_filter(message: str) -> str:
    sanitized = message
    for term, replacement in DIGNITY_REPLACEMENTS.items():
        sanitized = sanitized.replace(term, replacement)
    return sanitized


def check_gender_proxy(applicant: Dict[str, Any]) -> List[str]:
    violations = []
    for value in applicant.values():
        if isinstance(value, str):
            normalized = value.lower()
            for proxy in BLOCKED_PROXIES:
                if proxy in normalized:
                    violations.append(proxy)
    return list(set(violations))


def communication_limit(sent_today: int) -> bool:
    return sent_today < MAX_SMS_PER_DAY


def unusual_pattern_alert(current_rate: float, baseline_rate: float) -> bool:
    if baseline_rate <= 0:
        return False
    drop = baseline_rate - current_rate
    return drop / baseline_rate > UNUSUAL_PATTERN_DROP_THRESHOLD


def audit_trail_entry(applicant_name: str, decision: str, risk_score: int, bias_result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "applicant": applicant_name,
        "decision": decision,
        "risk_score": risk_score,
        "bias_result": bias_result,
    }
