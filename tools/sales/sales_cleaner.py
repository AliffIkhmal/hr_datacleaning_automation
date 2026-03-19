from __future__ import annotations

import pandas as pd

from core.industry_schemas import SALES_SCHEMA
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


class SalesCleaner(BaseCleaner):
    tool_name = "Sales Data Cleaner"
    description = "Clean sales datasets: deduplication, date formatting, outlier capping, category standardization."
    implemented = True

    def run(self, df: pd.DataFrame) -> CleaningResult:
        col_map = resolve_columns(df, SALES_SCHEMA)
        messages: list[str] = []

        # --- 1. Normalize missing placeholders ---
        working = normalize_missing_placeholders(df.copy())

        # --- 2. Remove duplicates ---
        working, dupes_removed = remove_duplicates(working)

        # --- 3. Standardize date columns ---
        date_cols = [
            col_map[c] for c in ("Order_Date", "Invoice_Date", "Close_Date", "Delivery_Date")
            if col_map.get(c) is not None
        ]
        working, dates_formatted = standardize_dates(working, date_cols)

        # --- 4. Correct negative values in monetary / quantity fields ---
        numeric_cols = [
            col_map[c] for c in (
                "Quantity_Sold", "Unit_Price", "Revenue", "Discount_Amount",
                "COGS", "Gross_Profit", "Commission_Amount", "Forecast_Amount",
            )
            if col_map.get(c) is not None
        ]
        working, negatives_fixed = correct_negatives(working, numeric_cols)

        # --- 5. Range validation ---
        range_rules: dict[str, tuple[float | None, float | None]] = {}
        if col_map.get("Quantity_Sold"):
            range_rules[col_map["Quantity_Sold"]] = (1, 100000)
        working, range_clipped = validate_ranges(working, range_rules)

        # --- 6. Outlier capping on Revenue via IQR ---
        outlier_cols = [
            col_map[c] for c in ("Revenue", "Unit_Price")
            if col_map.get(c) is not None
        ]
        working, outliers_df, outliers_detected = cap_outliers_iqr(working, outlier_cols)
        if not outliers_df.empty:
            messages.append(f"{outliers_detected} revenue/price outlier(s) capped using IQR method.")

        # --- 7. Standardise categorical columns ---
        cat_cols = [
            col_map[c] for c in (
                "Customer_Name", "Sales_Channel", "Region",
                "Product_Category", "Deal_Stage", "Payment_Term", "Order_Status",
            )
            if col_map.get(c) is not None
        ]
        working = standardize_categoricals(working, cat_cols)

        # --- 8. Fill missing values ---
        working, missing_fixed = fill_missing(working)

        # --- 9. Recalculate Revenue as abs(Price × Quantity) ---
        rev_col = col_map.get("Revenue")
        price_col = col_map.get("Unit_Price")
        qty_col = col_map.get("Quantity_Sold")
        derived_count = 0
        if rev_col and price_col and qty_col:
            can_calc = working[price_col].notna() & working[qty_col].notna()
            derived_count = int(can_calc.sum())
            if derived_count:
                working.loc[can_calc, rev_col] = (
                    working.loc[can_calc, price_col] * working.loc[can_calc, qty_col]
                ).abs()
                messages.append(f"{derived_count} revenue value(s) calculated from price × quantity.")

        # --- 10. Round numeric columns to whole numbers ---
        working = round_numeric_columns(working, decimals=2)

        # --- Build report ---
        stats = {
            "total_rows": len(working),
            "duplicates_removed": dupes_removed,
            "dates_formatted": dates_formatted,
            "negatives_corrected": negatives_fixed,
            "revenue_derived": derived_count,
            "range_values_clipped": range_clipped,
            "outliers_detected": outliers_detected,
            "missing_values_fixed": missing_fixed,
        }

        return CleaningResult(
            cleaned_df=working,
            report_df=build_report_dataframe(stats),
            stats=stats,
            issues_df=outliers_df if not outliers_df.empty else None,
            output_filename="cleaned_sales_dataset.csv",
            messages=messages,
        )