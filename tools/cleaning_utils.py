"""Shared cleaning utilities used across industry cleaners.

These are generic operations that apply to any tabular dataset:
- missing-placeholder normalisation
- duplicate removal
- negative value correction
- date standardisation
- IQR-based outlier capping
- categorical title-casing
"""

from __future__ import annotations

import re
from typing import Sequence

import numpy as np
import pandas as pd


MISSING_PLACEHOLDERS = {"", "-", "--", "na", "n/a", "nan", "null", "none", "missing", "undefined"}


# ------------------------------------------------------------------
# Missing placeholder normalisation
# ------------------------------------------------------------------

def normalize_missing_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.select_dtypes(include=["object", "category"]).columns:
        # Vectorized: astype(str) turns NaN→"nan" which is in MISSING_PLACEHOLDERS.
        lowered = out[col].astype(str).str.strip().str.lower()
        out.loc[lowered.isin(MISSING_PLACEHOLDERS), col] = np.nan
    return out


# ------------------------------------------------------------------
# Duplicate removal
# ------------------------------------------------------------------

def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(df)
    out = df.drop_duplicates().reset_index(drop=True)
    return out, before - len(out)


# ------------------------------------------------------------------
# Negative value correction
# ------------------------------------------------------------------

def correct_negatives(df: pd.DataFrame, columns: Sequence[str]) -> tuple[pd.DataFrame, int]:
    out = df.copy()
    total_corrected = 0
    for col in columns:
        if col in out.columns and pd.api.types.is_numeric_dtype(out[col]):
            mask = out[col] < 0
            total_corrected += int(mask.sum())
            out.loc[mask, col] = out.loc[mask, col].abs()
    return out, total_corrected


# ------------------------------------------------------------------
# Date standardisation
# ------------------------------------------------------------------

def standardize_dates(df: pd.DataFrame, columns: Sequence[str]) -> tuple[pd.DataFrame, int]:
    out = df.copy()
    formatted_count = 0
    for col in columns:
        if col not in out.columns:
            continue
        series = out[col]
        parsed = pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=False)
        unresolved = parsed.isna() & series.notna()
        if unresolved.any():
            parsed.loc[unresolved] = pd.to_datetime(
                series[unresolved], errors="coerce", format="mixed", dayfirst=True,
            )
        valid_count = int(parsed.notna().sum())
        if valid_count > 0:
            formatted_count += valid_count
            out[col] = parsed.dt.strftime("%Y-%m-%d")
    return out, formatted_count


# ------------------------------------------------------------------
# Outlier detection & capping (IQR)
# ------------------------------------------------------------------

def cap_outliers_iqr(
    df: pd.DataFrame,
    columns: Sequence[str],
    multiplier: float = 1.5,
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Cap outliers using IQR method. Returns (cleaned_df, outliers_df, count)."""
    out = df.copy()
    outlier_rows: list[pd.DataFrame] = []
    total = 0

    for col in columns:
        if col not in out.columns or not pd.api.types.is_numeric_dtype(out[col]):
            continue
        series = pd.to_numeric(out[col], errors="coerce")
        if series.dropna().count() < 10:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        mask = (series < lower) | (series > upper)
        count = int(mask.sum())
        if count > 0:
            outlier_rows.append(df.loc[mask].copy())
            total += count
            out.loc[series < lower, col] = lower
            out.loc[series > upper, col] = upper

    if outlier_rows:
        outliers_df = pd.concat(outlier_rows).drop_duplicates()
    else:
        outliers_df = pd.DataFrame()

    return out, outliers_df, total


# ------------------------------------------------------------------
# Range validation
# ------------------------------------------------------------------

def validate_ranges(
    df: pd.DataFrame,
    range_rules: dict[str, tuple[float | None, float | None]],
) -> tuple[pd.DataFrame, int]:
    """Clip numeric columns to [min, max] ranges. None means unbounded."""
    out = df.copy()
    total_clipped = 0
    for col, (lo, hi) in range_rules.items():
        if col not in out.columns or not pd.api.types.is_numeric_dtype(out[col]):
            continue
        series = pd.to_numeric(out[col], errors="coerce")
        before_clip = series.copy()
        series = series.clip(lower=lo, upper=hi)
        total_clipped += int((before_clip != series).sum())
        out[col] = series
    return out, total_clipped


# ------------------------------------------------------------------
# Categorical standardisation
# ------------------------------------------------------------------

def _smart_title(value: str) -> str:
    """Title-case each word, preserving all-uppercase words (acronyms/codes like HR, ID, USA)."""
    return " ".join(
        word if word.isupper() and len(word) > 1 else word.title()
        for word in value.strip().split()
    )


def standardize_categoricals(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            continue
        # Apply only to non-null rows; .map() is faster than .apply() for element-wise ops.
        mask = out[col].notna()
        if mask.any():
            out.loc[mask, col] = out[col][mask].map(_smart_title)
    return out


# ------------------------------------------------------------------
# Round all numeric columns to zero decimal places
# ------------------------------------------------------------------

def round_numeric_columns(df: pd.DataFrame, decimals: int = 0) -> pd.DataFrame:
    """Round every numeric column to `decimals` decimal places.
    When decimals=0, columns are also cast to nullable Int64."""
    out = df.copy()
    for col in out.select_dtypes(include=["number"]).columns:
        # Upcast to float64 first so float32 precision issues don't survive rounding.
        out[col] = out[col].astype("float64").round(decimals)
        if decimals == 0:
            try:
                out[col] = out[col].astype("Int64")
            except (ValueError, TypeError):
                pass
    return out


# ------------------------------------------------------------------
# Fill missing numeric with median, categorical with mode
# ------------------------------------------------------------------

def _looks_like_identifier(col: str, series: pd.Series) -> bool:
    """Return True if the column is likely an identifier that should not be imputed."""
    norm = re.sub(r"[^a-z0-9]+", "_", col.strip().lower()).strip("_")
    id_suffixes = ("_id", "_code", "_no", "_number", "_sku")
    if norm in ("id", "code", "no", "number", "sku") or any(norm.endswith(s) for s in id_suffixes):
        return True
    # High-uniqueness heuristic applies only to string columns (continuous numeric
    # fields like Temperature are also nearly all-unique but must be imputed).
    if pd.api.types.is_numeric_dtype(series):
        return False
    non_null = series.dropna()
    return len(non_null) >= 10 and float(non_null.nunique() / len(non_null)) >= 0.95


def fill_missing(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    out = df.copy()
    before = int(out.isna().sum().sum())

    for col in out.select_dtypes(include=["number"]).columns:
        if _looks_like_identifier(col, out[col]):
            continue
        median = out[col].median()
        out[col] = out[col].fillna(median)

    for col in out.select_dtypes(include=["object", "category"]).columns:
        if _looks_like_identifier(col, out[col]):
            continue
        mode = out[col].mode(dropna=True)
        if not mode.empty:
            out[col] = out[col].fillna(mode.iloc[0])

    after = int(out.isna().sum().sum())
    return out, before - after
