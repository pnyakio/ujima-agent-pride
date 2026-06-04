# UJIMA SACCO AGENT PRIDE PROTOTYPE

A capstone prototype demonstrating multi-agent orchestration, ethical AI governance, financial inclusion, human-in-the-loop lending support, and African data sovereignty.

## Installation

1. Create a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. Copy `.env.example` to `.env`.
2. Add your API keys for Cohere, Gemini, and Cerebras.
3. Set `LLM_DEFAULT_PROVIDER=Cohere` to use the primary provider.

## Running locally

```bash
streamlit run app.py
```

## Crew architecture

- `Scout` observes applicant context, detects stress, and never recommends loans.
- `Guardian` performs first-level screening, risk scoring, TRACK audit, and guardrail enforcement.
- `Hunter` prepares human-facing briefing packets without making final decisions.

## Agent descriptions

- `agents/scout_agent.py`: Financial literacy coach and harvest-cycle sentinel.
- `agents/guardian_agent.py`: Risk triage and bias auditing engine.
- `agents/hunter_agent.py`: Human-in-the-loop coordinator and briefing generator.

## Ethical governance design

The system preserves human accountability by always routing decisions to humans and never approving or denying loans automatically.
It applies dignity filtering, gender proxy blocking, and audit trail logging.

## TRACK framework

TRACK is implemented in `utils/bias_checker.py`:
- Training Data Audit
- Representation Audit
- Amplification Detection
- Counterfactual Testing
- Kill switch evaluation via guardrail conditions

## PRIDE oversight

The `app.py` dashboard visualizes the agent workflow, shows TRACK audit results, and displays guardrail status.

## RANK boundaries

RANK is encoded in `config/rank_rules.py` and protects the Scout, Guardian, and Hunter roles with clear authority and constraints.

## HUNT handoffs

The system escalates cases from Scout to Guardian when stress signals are detected, and from Guardian to Hunter when risk or loan size requires human review.

## GUARD safety rails

The safety layer includes:
- Gender proxy block
- Communication limit enforcement
- Unusual pattern detection
- Audit trail logging
- Dignity filter transformations

## Local operation

The pipeline runs locally in Streamlit and uses a cascading LLM fallback architecture for resilience.
