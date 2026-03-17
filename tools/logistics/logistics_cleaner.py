from __future__ import annotations

import pandas as pd

from core.industry_schemas import LOGISTICS_SCHEMA
from core.report_generator import build_report_dataframe
from core.schema_detector import resolve_columns
from tools.base import BaseCleaner, CleaningResult
from tools.cleaning_utils import (
    round_numeric_columns,
    cap_outliers_iqr,
    correct_negatives,
    fill_missing,
    normalize_missing_placeholders,
    remove_duplicates,
    standardize_categoricals,
    standardize_dates,
    validate_ranges,
)


class LogisticsCleaner(BaseCleaner):
    tool_name = "Logistics Data Cleaner"
    description = "Cleans shipment/delivery datasets: weight & distance validation, delay detection, date formatting, deduplication."
    implemented = True

    def run(self, df: pd.DataFrame) -> CleaningResult:
        col_map = resolve_columns(df, LOGISTICS_SCHEMA)
        messages: list[str] = []

        # --- 1. Normalise missing placeholders ---
        working = normalize_missing_placeholders(df.copy())

        # --- 2. Remove duplicates ---
        working, dupes_removed = remove_duplicates(working)

        # --- 3. Standardise date columns ---
        date_cols = [
            col_map[c] for c in (
                "Shipment_Date", "Estimated_Delivery_Date",
                "Actual_Delivery_Date", "Pickup_Timestamp", "Scan_Timestamp",
            )
            if col_map.get(c) is not None
        ]
        working, dates_formatted = standardize_dates(working, date_cols)

        # --- 4. Correct negatives ---
        numeric_cols = [
            col_map[c] for c in (
                "Shipment_Weight_KG", "Shipment_Volume_CBM", "Distance_KM",
                "Freight_Cost", "Delivery_Time_Hours", "Delay_Minutes",
                "Packages_Count", "Fuel_Cost",
            )
            if col_map.get(c) is not None
        ]
        working, negatives_fixed = correct_negatives(working, numeric_cols)

        # --- 5. Range validation ---
        range_rules: dict[str, tuple[float | None, float | None]] = {}
        if col_map.get("Packages_Count"):
            range_rules[col_map["Packages_Count"]] = (1, None)
        working, range_clipped = validate_ranges(working, range_rules)

        # --- 6. Outlier capping on freight cost and distance ---
        outlier_cols = [
            col_map[c] for c in ("Freight_Cost", "Distance_KM", "Delivery_Time_Hours")
            if col_map.get(c) is not None
        ]
        working, outliers_df, outliers_detected = cap_outliers_iqr(working, outlier_cols)
        if not outliers_df.empty:
            messages.append(f"{outliers_detected} logistics outlier(s) capped using IQR method.")

        # --- 7. Standardise categorical columns ---
        cat_cols = [
            col_map[c] for c in (
                "Origin_Location", "Destination_Location", "Carrier_Name",
                "Delivery_Status", "Transport_Mode", "Service_Level", "Return_Flag",
            )
            if col_map.get(c) is not None
        ]
        working = standardize_categoricals(working, cat_cols)

        # --- 8. Fill missing values ---
        working, missing_fixed = fill_missing(working)

        # --- 9. Round numeric columns to whole numbers ---
        working = round_numeric_columns(working)

        # --- Build report ---
        stats = {
            "total_rows": len(working),
            "duplicates_removed": dupes_removed,
            "dates_formatted": dates_formatted,
            "negatives_corrected": negatives_fixed,
            "range_values_clipped": range_clipped,
            "outliers_detected": outliers_detected,
            "missing_values_fixed": missing_fixed,
        }

        return CleaningResult(
            cleaned_df=working,
            report_df=build_report_dataframe(stats),
            stats=stats,
            issues_df=outliers_df if not outliers_df.empty else None,
            output_filename="cleaned_logistics_dataset.csv",
            messages=messages,
        )