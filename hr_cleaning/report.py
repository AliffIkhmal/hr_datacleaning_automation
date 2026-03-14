from __future__ import annotations

from typing import Dict

import pandas as pd


REPORT_LABELS = {
    "total_rows": "Total Rows",
    "duplicates_removed": "Duplicates Removed",
    "missing_values_fixed": "Missing Values Fixed",
    "negative_values_corrected": "Negative Values Corrected",
    "gender_inferred_by_name": "Gender Inferred By Name",
    "single_digit_ages_replaced": "Single-Digit Ages Replaced",
    "performance_rating_capped": "Performance Rating Capped",
    "outliers_detected": "Salary Outliers Detected",
    "salary_outliers_handled": "Salary Outliers Handled",
}


def generate_cleaning_report(stats: Dict[str, int]) -> pd.DataFrame:
    rows = []
    for key, label in REPORT_LABELS.items():
        rows.append({"Metric": label, "Value": int(stats.get(key, 0))})

    return pd.DataFrame(rows)
