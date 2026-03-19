from __future__ import annotations

import re
from typing import Any

import pandas as pd

from core.industry_schemas import INDUSTRY_SCHEMAS, IndustrySchema


DATE_NAME_PATTERNS = ("date", "time", "timestamp", "month", "year", "day")
IDENTIFIER_NAME_PATTERNS = (
    "id",
    "code",
    "number",
    "no",
    "sku",
    "employee",
    "order",
)
RULE_PATTERNS = {
    "outlier_detection": {
        "keywords": {"salary", "wage", "income", "amount", "cost", "price", "revenue"},
        "suggestion": "Outlier detection",
        "reason": "Potential monetary field.",
    },
    "date_formatting": {
        "keywords": {"date", "time", "timestamp", "hire", "ship", "delivery", "created"},
        "suggestion": "Date formatting",
        "reason": "Potential date or timestamp field.",
    },
    "range_validation": {
        "keywords": {"age", "rating", "score", "quantity", "hours", "stock"},
        "suggestion": "Range validation",
        "reason": "Potential bounded numeric field.",
    },
    "duplicate_detection": {
        "keywords": {"id", "code", "number", "employee", "customer", "order", "sku"},
        "suggestion": "Duplicate detection",
        "reason": "Potential identifier field.",
    },
    "missing_value_review": {
        "keywords": {"name", "gender", "department", "status", "category", "region"},
        "suggestion": "Missing value review",
        "reason": "Potential categorical business field.",
    },
    "derived_calculation": {
        "keywords": {"total", "gross", "net", "subtotal", "margin", "profit"},
        "suggestion": "Derived field recalculation",
        "reason": "Potential computed field (e.g. price × quantity).",
    },
    "negative_correction": {
        "keywords": {"price", "cost", "fee", "freight", "weight", "distance"},
        "suggestion": "Negative value correction",
        "reason": "Field should not contain negative values.",
    },
}


def _normalize_column_name(column_name: Any) -> str:
    normalized = str(column_name).strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def _parseable_datetime_ratio(series: pd.Series, sample_size: int = 50) -> float:
    non_null = series.dropna()
    if non_null.empty:
        return 0.0

    sample = non_null.astype(str).head(sample_size)
    parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
    return float(parsed.notna().mean())


def detect_numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["number"]).columns.tolist()


def detect_categorical_columns(df: pd.DataFrame) -> list[str]:
    categorical_df = df.select_dtypes(include=["object", "category", "bool"])
    return categorical_df.columns.tolist()


def detect_potential_date_columns(df: pd.DataFrame) -> list[str]:
    detected_columns: list[str] = []

    for column in df.columns:
        normalized = _normalize_column_name(column)
        if any(pattern in normalized for pattern in DATE_NAME_PATTERNS):
            detected_columns.append(column)
            continue

        if _parseable_datetime_ratio(df[column]) >= 0.6:
            detected_columns.append(column)

    return detected_columns


def detect_identifier_columns(df: pd.DataFrame) -> list[str]:
    identifier_columns: list[str] = []

    for column in df.columns:
        normalized = _normalize_column_name(column)
        series = df[column]
        uniqueness_ratio = float(series.nunique(dropna=True) / max(len(series.dropna()), 1))

        if any(pattern in normalized for pattern in IDENTIFIER_NAME_PATTERNS):
            identifier_columns.append(column)
            continue

        if uniqueness_ratio >= 0.95 and series.notna().any():
            identifier_columns.append(column)

    return identifier_columns


def suggest_cleaning_rules(df: pd.DataFrame) -> list[dict[str, str]]:
    suggestions: list[dict[str, str]] = []

    for column in df.columns:
        normalized = _normalize_column_name(column)
        for rule in RULE_PATTERNS.values():
            if any(keyword in normalized for keyword in rule["keywords"]):
                suggestions.append(
                    {
                        "Column": str(column),
                        "Suggested Rule": rule["suggestion"],
                        "Reason": rule["reason"],
                    }
                )

    return suggestions


def detect_schema(df: pd.DataFrame) -> dict[str, object]:
    return {
        "numeric_columns": detect_numeric_columns(df),
        "categorical_columns": detect_categorical_columns(df),
        "potential_date_columns": detect_potential_date_columns(df),
        "identifier_columns": detect_identifier_columns(df),
        "suggested_rules": suggest_cleaning_rules(df),
        "detected_industry": detect_industry(df),
    }


# ---------------------------------------------------------------------------
# Industry detection via alias matching against INDUSTRY_SCHEMAS
# ---------------------------------------------------------------------------

def _build_alias_pool(schema: IndustrySchema) -> dict[str, set[str]]:
    """Return {canonical_name: set_of_normalized_aliases} for every column."""
    pool: dict[str, set[str]] = {}
    for canonical, info in schema["columns"].items():
        aliases = {_normalize_column_name(a) for a in info["aliases"]}
        aliases.add(_normalize_column_name(canonical))
        pool[canonical] = aliases
    return pool


def resolve_columns(
    df: pd.DataFrame,
    schema: IndustrySchema,
) -> dict[str, str | None]:
    """Map each canonical column in *schema* to an actual df column (or None)."""
    pool = _build_alias_pool(schema)
    normalized_df_cols = {_normalize_column_name(c): c for c in df.columns}

    mapping: dict[str, str | None] = {}
    for canonical, aliases in pool.items():
        match = None
        for alias in aliases:
            if alias in normalized_df_cols:
                match = normalized_df_cols[alias]
                break
        mapping[canonical] = match
    return mapping


def detect_industry(df: pd.DataFrame) -> str | None:
    """Return the best-matching industry name, or None if no schema matches.

    Primary score: number of required columns matched.
    Tie-breaker: total columns matched (including non-required), favouring
    the schema whose full column pool aligns best with the dataset.
    """
    best_industry: str | None = None
    best_required = 0
    best_total = 0

    for name, schema in INDUSTRY_SCHEMAS.items():
        col_map = resolve_columns(df, schema)
        required = schema["required_columns"]
        required_matched = sum(1 for r in required if col_map.get(r) is not None)
        if required_matched < schema["min_required"]:
            continue
        total_matched = sum(1 for v in col_map.values() if v is not None)
        if (
            required_matched > best_required
            or (required_matched == best_required and total_matched > best_total)
        ):
            best_required = required_matched
            best_total = total_matched
            best_industry = name

    return best_industry