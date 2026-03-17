from __future__ import annotations

import pandas as pd

from core.industry_schemas import MANUFACTURING_SCHEMA
from core.report_generator import build_report_dataframe
from core.schema_detector import resolve_columns
from tools.base import BaseCleaner, CleaningResult
from tools.cleaning_utils import (
    cap_outliers_iqr,
    correct_negatives,
    fill_missing,
    normalize_missing_placeholders,
    remove_duplicates,
    round_numeric_columns,
    standardize_categoricals,
    standardize_dates,
    validate_ranges,
)


class ManufacturingCleaner(BaseCleaner):
    tool_name = "Manufacturing Data Cleaner"
    description = "Cleans production/quality datasets: defect-rate validation, cycle-time outliers, date formatting, deduplication."
    implemented = True

    def run(self, df: pd.DataFrame) -> CleaningResult:
        col_map = resolve_columns(df, MANUFACTURING_SCHEMA)
        messages: list[str] = []

        # --- 1. Normalise missing placeholders ---
        working = normalize_missing_placeholders(df.copy())

        # --- 2. Remove duplicates ---
        working, dupes_removed = remove_duplicates(working)

        # --- 3. Standardise date columns ---
        date_cols = [
            col_map[c] for c in (
                "Production_Date", "Start_Timestamp", "End_Timestamp", "Maintenance_Date",
            )
            if col_map.get(c) is not None
        ]
        working, dates_formatted = standardize_dates(working, date_cols)

        # --- 4. Correct negatives in quantity / time fields ---
        numeric_cols = [
            col_map[c] for c in (
                "Planned_Quantity", "Produced_Quantity", "Scrap_Quantity",
                "Cycle_Time_Minutes", "Downtime_Minutes", "Unit_Cost",
                "Temperature",
            )
            if col_map.get(c) is not None
        ]
        working, negatives_fixed = correct_negatives(working, numeric_cols)

        # --- 5. Range validation ---
        range_rules: dict[str, tuple[float | None, float | None]] = {}
        if col_map.get("Defect_Rate"):
            dr_col = col_map["Defect_Rate"]
            dr_series = pd.to_numeric(working[dr_col], errors="coerce").dropna()
            if not dr_series.empty and dr_series.max() <= 1.0:
                working[dr_col] = pd.to_numeric(working[dr_col], errors="coerce") * 100
                messages.append("Defect_Rate detected as ratio (0–1); converted to percentage (0–100).")
            range_rules[dr_col] = (0, 100)
        if col_map.get("Yield_Percent"):
            range_rules[col_map["Yield_Percent"]] = (0, 100)
        working, range_clipped = validate_ranges(working, range_rules)

        # --- 6. Outlier capping on cycle time, unit cost, and temperature ---
        outlier_cols = [
            col_map[c] for c in ("Cycle_Time_Minutes", "Unit_Cost", "Downtime_Minutes", "Temperature")
            if col_map.get(c) is not None
        ]
        working, outliers_df, outliers_detected = cap_outliers_iqr(working, outlier_cols)
        if not outliers_df.empty:
            messages.append(f"{outliers_detected} production outlier(s) capped using IQR method.")

        # --- 7. Standardize categorical columns ---
        cat_cols = [
            col_map[c] for c in (
                "Product_Name", "Product_Category", "Shift",
                "Machine_Status", "Defect_Type", "Operator_Name", "Plant_Name",
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
            output_filename="cleaned_manufacturing_dataset.csv",
            messages=messages,
        )