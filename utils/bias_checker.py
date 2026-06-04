from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import pandas as pd


@dataclass
class BiasAuditResult:
    training_data: Dict[str, Any]
    representation: Dict[str, Any]
    amplification: Dict[str, Any]
    counterfactual: Dict[str, Any]


class BiasChecker:
    def __init__(self, sample_path: Path | str = "data/sample_applications.csv") -> None:
        self.sample_path = Path(sample_path)
        self.sample_df = self._load_sample_data()

    def _load_sample_data(self) -> pd.DataFrame:
        if self.sample_path.exists():
            return pd.read_csv(self.sample_path)
        return pd.DataFrame()

    def run_track_audit(self, applicant: Dict[str, Any], risk_score: int) -> Dict[str, Any]:
        return {
            "training_data": self.training_data_audit(),
            "representation": self.representation_audit(applicant),
            "amplification": self.amplification_detection(applicant, risk_score),
            "counterfactual": self.counterfactual_test(applicant, risk_score),
            "bias_flags": self._bias_flags(applicant, risk_score),
        }

    def training_data_audit(self) -> Dict[str, Any]:
        if self.sample_df.empty:
            return {"note": "Sample application data is unavailable."}

        vendor_count = self.sample_df["occupation"].str.contains("vendor", case=False, na=False).sum()
        formal_count = self.sample_df["occupation"].str.contains("employee|teacher|government", case=False, na=False).sum()
        return {
            "total_records": len(self.sample_df),
            "market_vendor_share": float(vendor_count) / len(self.sample_df) if len(self.sample_df) else 0.0,
            "formal_employee_share": float(formal_count) / len(self.sample_df) if len(self.sample_df) else 0.0,
        }

    def representation_audit(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        if self.sample_df.empty:
            return {"note": "No representation baseline available."}

        county = applicant.get("county", "Unknown")
        county_rate = float((self.sample_df["county"].str.lower() == county.lower()).sum()) / len(self.sample_df)
        baseline_rate = 1.0 / max(len(self.sample_df["county"].unique()), 1)
        return {
            "county": county,
            "county_rate": county_rate,
            "baseline_rate": baseline_rate,
            "representation_gap": county_rate - baseline_rate,
        }

    def amplification_detection(self, applicant: Dict[str, Any], risk_score: int) -> Dict[str, Any]:
        purpose = applicant.get("purpose", "").lower()
        findings = {}
        if "loan shark" in purpose:
            findings["loan_shark"] = "Applicant language suggests predatory lending awareness."
        if "school fees" in purpose:
            findings["school_fees"] = "School fee pressure may amplify repayment risk."
        if risk_score >= 70:
            findings["risk_amplification"] = "Higher risk score may amplify conservative outcomes."
        return findings

    def counterfactual_test(self, applicant: Dict[str, Any], risk_score: int) -> Dict[str, Any]:
        alternative = dict(applicant)
        alternative["occupation"] = "Formal Employee"
        alternative_score = self._estimate_risk_score(alternative)
        delta = abs(risk_score - alternative_score)
        bias_flag = delta >= 12
        return {
            "original_score": risk_score,
            "counterfactual_score": alternative_score,
            "occupation_replacement": "Formal Employee",
            "score_delta": delta,
            "bias_flag": bias_flag,
        }

    def _estimate_risk_score(self, applicant: Dict[str, Any]) -> int:
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
        if "loan shark" in purpose:
            score += 8

        if income > 30000 and savings > 15000:
            score -= 10

        return max(min(score, 100), 0)

    def _bias_flags(self, applicant: Dict[str, Any], risk_score: int) -> Dict[str, bool]:
        return {
            "occupation_bias": "vendor" in applicant.get("occupation", "").lower() and risk_score >= 70,
            "county_bias": self.representation_audit(applicant).get("representation_gap", 0.0) < -0.25,
            "counterfactual_bias": self.counterfactual_test(applicant, risk_score).get("bias_flag", False),
        }
