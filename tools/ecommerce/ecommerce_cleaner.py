from __future__ import annotations

import pandas as pd

from core.industry_schemas import ECOMMERCE_SCHEMA
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


class EcommerceCleaner(BaseCleaner):
    tool_name = "E-commerce Data Cleaner"
    description = "Cleans order/transaction datasets: order-value outliers, quantity validation, date formatting, deduplication."
    implemented = True

    def run(self, df: pd.DataFrame) -> CleaningResult:
        col_map = resolve_columns(df, ECOMMERCE_SCHEMA)
        messages: list[str] = []

        # --- 1. Normalise missing placeholders ---
        working = normalize_missing_placeholders(df.copy())

        # --- 2. Remove duplicates ---
        working, dupes_removed = remove_duplicates(working)

        # --- 3. Standardise date columns ---
        date_cols = [
            col_map[c] for c in (
                "Order_Date", "Payment_Date", "Shipment_Date",
                "Delivery_Date", "Return_Date",
            )
            if col_map.get(c) is not None
        ]
        working, dates_formatted = standardize_dates(working, date_cols)

        # --- 4. Correct negatives ---
        numeric_cols = [
            col_map[c] for c in (
                "Quantity", "Unit_Price", "Tax_Amount",
                "Shipping_Fee", "Order_Value", "Inventory_On_Hand",
            )
            if col_map.get(c) is not None
        ]
        working, negatives_fixed = correct_negatives(working, numeric_cols)

        # --- 5. Range validation ---
        range_rules: dict[str, tuple[float | None, float | None]] = {}
        if col_map.get("Quantity"):
            range_rules[col_map["Quantity"]] = (1, 10000)
        if col_map.get("Customer_Rating"):
            range_rules[col_map["Customer_Rating"]] = (1, 5)
        working, range_clipped = validate_ranges(working, range_rules)

        # --- 6. Outlier capping on order value and unit price ---
        outlier_cols = [
            col_map[c] for c in ("Order_Value", "Unit_Price")
            if col_map.get(c) is not None
        ]
        working, outliers_df, outliers_detected = cap_outliers_iqr(working, outlier_cols)
        if not outliers_df.empty:
            messages.append(f"{outliers_detected} order-value/price outlier(s) capped using IQR method.")

        # --- 7. Standardise categorical columns ---
        cat_cols = [
            col_map[c] for c in (
                "Customer_Name", "Product_Name", "Product_Category",
                "Payment_Method", "Order_Status", "Device_Type",
                "Traffic_Source", "Coupon_Code",
            )
            if col_map.get(c) is not None
        ]
        working = standardize_categoricals(working, cat_cols)

        # --- 8. Fill missing values ---
        working, missing_fixed = fill_missing(working)

        # --- 9. Recalculate Order_Value as abs(Price × Quantity) ---
        val_col = col_map.get("Order_Value")
        price_col = col_map.get("Unit_Price")
        qty_col = col_map.get("Quantity")
        derived_count = 0
        if price_col and qty_col:
            can_calc = working[price_col].notna() & working[qty_col].notna()
            derived_count = int(can_calc.sum())
            # If Order_Value column doesn't exist yet, create it
            if val_col is None:
                val_col = "Order_Value"
                working[val_col] = pd.NA
            if derived_count:
                working.loc[can_calc, val_col] = (
                    working.loc[can_calc, price_col] * working.loc[can_calc, qty_col]
                ).abs()
                messages.append(f"{derived_count} order value(s) calculated from price × quantity.")

        # --- 10. Round numeric columns to whole numbers ---
        working = round_numeric_columns(working)

        # --- Build report ---
        stats = {
            "total_rows": len(working),
            "duplicates_removed": dupes_removed,
            "dates_formatted": dates_formatted,
            "negatives_corrected": negatives_fixed,
            "order_value_derived": derived_count,
            "range_values_clipped": range_clipped,
            "outliers_detected": outliers_detected,
            "missing_values_fixed": missing_fixed,
        }

        return CleaningResult(
            cleaned_df=working,
            report_df=build_report_dataframe(stats),
            stats=stats,
            issues_df=outliers_df if not outliers_df.empty else None,
            output_filename="cleaned_ecommerce_dataset.csv",
            messages=messages,
        )