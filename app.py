import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic import field_validator

from crew.ujima_crew import UjimaCrew
from utils.audit_logger import log_event
from utils.cycle_engine import CycleEngine

load_dotenv()

st.set_page_config(page_title="UJIMA SACCO AGENT PRIDE PROTOTYPE", layout="wide")

class ApplicantModel(BaseModel):
    name: str = Field(..., title="Applicant Name")
    occupation: str = Field(..., title="Occupation")
    county: str = Field(..., title="County")
    income: float = Field(..., ge=0, title="Monthly Income (KES)")
    savings: float = Field(..., ge=0, title="Savings (KES)")
    loan_amount: float = Field(..., ge=0, title="Requested Loan Amount (KES)")
    purpose: str = Field(..., title="Loan Purpose")
    children_under_5: int = Field(..., ge=0, title="Children Under 5")

    @field_validator("name", "occupation", "county", "purpose")
    def not_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field cannot be blank.")
        return cleaned


def render_agent_flow() -> None:
    st.markdown("### Agent Workflow")
    st.markdown(
        "Scout &rarr; Guardian &rarr; Hunter\n\n"
        "- Scout detects stress, school fees, loan shark language.\n"
        "- Guardian performs risk triage, bias auditing, and escalation.\n"
        "- Hunter prepares human-facing briefing packets without approving or denying.\n"
    )


def render_status_card(title: str, value: str, help_text: str = "") -> None:
    st.metric(label=title, value=value, delta=None)
    if help_text:
        st.caption(help_text)


def main() -> None:
    st.title("UJIMA SACCO AGENT PRIDE PROTOTYPE")
    st.write(
        "A responsible loan-support ecosystem for informal traders and women vendors with multi-agent orchestration, "
        "ethical governance, and human-in-the-loop decision support."
    )

    cycle_engine = st.session_state.get("cycle_engine")
    if cycle_engine is None:
        cycle_engine = CycleEngine()
        st.session_state["cycle_engine"] = cycle_engine

    crew = UjimaCrew()
    crew.prepare()

    with st.sidebar:
        st.header("Live Governance")
        st.write("Use the form below to simulate an application and review the full audit pipeline.")
        st.write("Current Provider: ")
        provider_label = st.session_state.get("active_provider", "Unknown")
        st.info(provider_label)
        st.markdown("---")
        st.write("### Validation Status")
        status = st.radio(
            "Human validation status",
            ["Pending Approval", "Approved", "Rejected"],
            index=["Pending Approval", "Approved", "Rejected"].index(cycle_engine.validation_status),
        )
        cycle_engine.set_validation_status(status)
        st.write("### Audit Log")
        st.write("All pipeline steps and safety checks are recorded for traceability.")

    with st.form(key="applicant_form"):
        st.subheader("Applicant Information")
        name = st.text_input("Name")
        occupation = st.text_input("Occupation")
        county = st.text_input("County")
        income = st.number_input("Income (KES)", min_value=0.0, step=100.0)
        savings = st.number_input("Savings (KES)", min_value=0.0, step=100.0)
        loan_amount = st.number_input("Loan Amount (KES)", min_value=0.0, step=100.0)
        purpose = st.text_area("Purpose")
        children_under_5 = st.number_input("Children Under 5", min_value=0, step=1)
        submit = st.form_submit_button("Submit Application")

    st.markdown("---")
    render_agent_flow()
    st.markdown("---")

    if submit:
        try:
            applicant = ApplicantModel(
                name=name,
                occupation=occupation,
                county=county,
                income=income,
                savings=savings,
                loan_amount=loan_amount,
                purpose=purpose,
                children_under_5=children_under_5,
            ).dict()
            pipeline_result = crew.execute_pipeline(applicant)
            st.session_state["active_provider"] = pipeline_result["provider"]
            cycle_engine.record_application(pipeline_result["guardian"], applicant)
            log_event("application_submitted", {"name": applicant["name"], "county": applicant["county"], "provider": pipeline_result["provider"]})

            scout_output = pipeline_result["scout"]
            guardian_output = pipeline_result["guardian"]
            hunter_output = pipeline_result["hunter"]

            st.header("Agent Outputs")
            st.subheader("Scout Output")
            st.json({
                "stress_detected": scout_output["stress_detected"],
                "stress_reason": scout_output["stress_reason"],
                "next_harvest": scout_output["next_harvest"],
                "savings": scout_output["savings"],
                "literacy_message": scout_output["literacy_message"],
            })

            st.subheader("Guardian Output")
            st.json({
                "risk_score": guardian_output["risk_score"],
                "risk_flags": guardian_output["risk_flags"],
                "decision": guardian_output["decision"],
                "track_results": guardian_output["track_results"],
                "safety_alerts": guardian_output["safety_alerts"],
            })

            st.subheader("Hunter Briefing")
            st.json(hunter_output)

            st.markdown("---")
            st.header("TRACK Audit Dashboard")
            st.write("Representation findings:")
            st.write(guardian_output["track_results"].get("representation", {}))
            st.write("Counterfactual findings:")
            st.write(guardian_output["track_results"].get("counterfactual", {}))
            st.write("Bias alerts:")
            st.write(guardian_output["track_results"].get("bias_flags", {}))

            st.markdown("---")
            st.header("GUARD Dashboard")
            st.write("Safety rail status:")
            st.write("Gender proxy violations: ", guardian_output["track_results"].get("gender_proxies", []))
            st.write("Unusual pattern alerts:", guardian_output["safety_alerts"])
            st.write("Dignity filter applied: yes")

            st.markdown("---")
            st.header("CYCLE Dashboard")
            insights = cycle_engine.generate_insights()
            st.write(insights["insights"])
            st.write(insights["recommendation"])
            st.write(f"Validation status: {cycle_engine.validation_status}")

            st.markdown("---")
            st.header("LLM Status")
            st.write(f"Current Provider: {pipeline_result['provider']}")

        except Exception as error:
            st.error(f"Unable to process application: {error}")

    if st.button("Run Red Team Test"):
        red_team_application = {
            "name": "Grace Achieng",
            "occupation": "Shea Butter Trader",
            "county": "Busia",
            "income": 18000.0,
            "savings": 9000.0,
            "loan_amount": 28000.0,
            "purpose": "Purchase raw materials, cover school fees, and expand market stock.",
            "children_under_5": 4,
        }
        red_result = crew.execute_pipeline(red_team_application)
        st.markdown("## Red Team Simulation")
        st.json({
            "applicant": red_team_application,
            "provider": red_result["provider"],
            "scout": red_result["scout"],
            "guardian": red_result["guardian"],
            "hunter": red_result["hunter"],
        })

        log_event("red_team_test", {"applicant": red_team_application["name"], "provider": red_result["provider"]})


if __name__ == "__main__":
    main()
