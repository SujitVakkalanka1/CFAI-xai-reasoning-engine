"""
Finance reasoning model for an academic project.

The model reads financial details, checks them against a small set of
finance-focused conditions, and returns a clear result with plain-language
reasons.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class FinanceInputError(Exception):
    """Raised when the entered financial details are missing or invalid."""


class FinanceReasoningModel:
    """Simple finance reasoning model with plain-language explanations."""

    required_fields = {
        "monthly_income": "Monthly income",
        "monthly_expenses": "Monthly living costs",
        "monthly_debt_payments": "Monthly debt payments",
        "credit_score": "Credit score",
        "missed_payments_12m": "Missed payments in last 12 months",
        "emergency_savings_months": "Emergency savings in months",
    }

    severity_labels = {
        0: "Good position",
        1: "Needs attention",
        2: "High concern",
    }

    result_text = {
        0: "This case looks financially stable based on the entered values.",
        1: "This case may be acceptable, but it needs a closer look.",
        2: "This case should be reviewed carefully before approval.",
    }

    def __init__(self, checks: List[Dict[str, Any]]):
        self.checks = checks

    @classmethod
    def from_json(cls, path: str | Path) -> "FinanceReasoningModel":
        path = Path(path)
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return cls(data["checks"])

    def evaluate(self, entered_values: Dict[str, Any]) -> Dict[str, Any]:
        values = self._clean_values(entered_values)
        numbers = self._add_simple_calculations(values)

        matched_checks: List[Dict[str, Any]] = []

        for check in self.checks:
            if self._check_matches(check, numbers):
                matched_checks.append({
                    "id": check["id"],
                    "title": check["title"],
                    "message": check["message"],
                    "severity": int(check["severity"]),
                    "area": check.get("area", "general"),
                })

        concern_checks = [item for item in matched_checks if item["severity"] > 0]
        good_checks = [item for item in matched_checks if item["severity"] == 0]

        final_severity = max(
            [item["severity"] for item in concern_checks],
            default=0,
        )

        return {
            "result": {
                "level": self.severity_labels[final_severity],
                "message": self.result_text[final_severity],
            },
            "reasons": concern_checks,
            "positive_points": good_checks,
            "next_steps": self._build_next_steps(concern_checks),
            "numbers": {
                "monthly_income": round(numbers["monthly_income"], 2),
                "monthly_expenses": round(numbers["monthly_expenses"], 2),
                "monthly_debt_payments": round(numbers["monthly_debt_payments"], 2),
                "money_left": round(numbers["money_left"], 2),
                "debt_percent": round(numbers["debt_percent"], 1),
                "money_left_percent": round(numbers["money_left_percent"], 1),
            },
        }

    def _clean_values(self, entered_values: Dict[str, Any]) -> Dict[str, float]:
        if not isinstance(entered_values, dict):
            raise FinanceInputError("Please enter the financial details correctly.")

        cleaned: Dict[str, float] = {}

        for field, label in self.required_fields.items():
            if field not in entered_values:
                raise FinanceInputError(f"{label} is missing.")

            try:
                cleaned[field] = float(entered_values[field])
            except (TypeError, ValueError):
                raise FinanceInputError(f"{label} must be a number.")

        if cleaned["monthly_income"] <= 0:
            raise FinanceInputError("Monthly income must be greater than 0.")

        if not 300 <= cleaned["credit_score"] <= 900:
            raise FinanceInputError("Credit score should be between 300 and 900.")

        for field in [
            "monthly_expenses",
            "monthly_debt_payments",
            "missed_payments_12m",
            "emergency_savings_months",
        ]:
            if cleaned[field] < 0:
                label = self.required_fields[field]
                raise FinanceInputError(f"{label} cannot be negative.")

        return cleaned

    def _add_simple_calculations(self, values: Dict[str, float]) -> Dict[str, float]:
        numbers = dict(values)

        income = numbers["monthly_income"]
        debt = numbers["monthly_debt_payments"]
        expenses = numbers["monthly_expenses"]

        money_left = income - expenses - debt

        numbers["money_left"] = money_left
        numbers["debt_percent"] = (debt / income) * 100
        numbers["money_left_percent"] = (money_left / income) * 100

        return numbers

    def _check_matches(self, check: Dict[str, Any], numbers: Dict[str, float]) -> bool:
        return all(
            self._compare(
                actual=numbers[condition["field"]],
                operator=condition["operator"],
                expected=condition["value"],
            )
            for condition in check["conditions"]
        )

    def _compare(self, actual: float, operator: str, expected: float) -> bool:
        if operator == "<":
            return actual < expected
        if operator == "<=":
            return actual <= expected
        if operator == ">":
            return actual > expected
        if operator == ">=":
            return actual >= expected
        if operator == "==":
            return actual == expected

        raise FinanceInputError(f"Unsupported comparison: {operator}")

    def _build_next_steps(self, concern_checks: List[Dict[str, Any]]) -> List[str]:
        if not concern_checks:
            return [
                "Keep debt payments manageable.",
                "Maintain emergency savings.",
                "Continue paying on time.",
            ]

        steps_by_area = {
            "credit": "Improve payment history before taking new credit.",
            "debt": "Lower monthly debt payments where possible.",
            "cash": "Increase the money left after monthly costs.",
            "savings": "Build emergency savings of at least 3 months.",
        }

        steps = []
        used_areas = set()

        for item in concern_checks:
            area = item["area"]
            if area in steps_by_area and area not in used_areas:
                steps.append(steps_by_area[area])
                used_areas.add(area)

        return steps or ["Review the weak areas before making a finance decision."]
