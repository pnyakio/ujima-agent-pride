# Rank Documentation

RANK calibration defines the boundaries for each agent role in the Ujima prototype.

- Scout: Financial Literacy Coach
  - Role: Educate members, harvest cycle planning, and detect stress.
  - Authority: Maximum 3 SMS/day, never recommend loans.
  - Kill switch: `*#700#`

- Guardian: Loan Triage Agent
  - Role: First-level screening, risk scoring, bias audit, and guardrail verification.
  - Authority: Approve only loans ≤ 15000 KES, deny only when 3+ risk flags exist.
  - Kill switch: `*#733#`

- Hunter: Human-In-The-Loop Coordinator
  - Role: Coordinate officers, prepare briefing packets, and maintain accountability.
  - Authority: Cannot approve or deny.
  - Kill switch: `*#799#`

The RANK documentation helps keep responsibility, authority, and notice boundaries explicit across the agent chain.
