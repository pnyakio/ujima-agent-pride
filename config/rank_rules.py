from dataclasses import dataclass


@dataclass(frozen=True)
class RankRule:
    role: str
    authority: str
    kill_switch: str
    notes: str


SCOUT_RULES = RankRule(
    role="Financial Literacy Coach",
    authority="Maximum 3 SMS/day. Never recommend loans.",
    kill_switch="*#700#",
    notes="Detect early financial stress, harvest timing, and refer only when risk indicators appear.",
)

GUARDIAN_RULES = RankRule(
    role="Loan Triage Agent",
    authority="Approve only loans ≤ 15000 KES. Deny only if 3+ risk flags exist.",
    kill_switch="*#733#",
    notes="Conduct first-level screening, calculate risk scores, and apply TRACK audit before escalation.",
)

HUNTER_RULES = RankRule(
    role="Human-In-The-Loop Coordinator",
    authority="Cannot approve. Cannot deny.",
    kill_switch="*#799#",
    notes="Prepare human briefings, coordinate officers, and preserve accountability through review packets.",
)


def guardian_needs_escalation(children_under_5: int, loan_amount: float, mentions_debt_collector: bool) -> bool:
    return loan_amount > 15000 or children_under_5 >= 2 or mentions_debt_collector


def scout_should_notify_guardian(purpose: str) -> bool:
    keywords = ["loan shark", "school fees", "financial stress", "late payment", "collector"]
    return any(keyword in purpose.lower() for keyword in keywords)
