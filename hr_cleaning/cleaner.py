from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd


NEGATIVE_CHECK_COLUMNS = ["Age", "Salary", "Overtime_Hours"]
DATE_COLUMNS = ["Hire_Date"]
MISSING_PLACEHOLDERS = {"", "-", "--", "na", "n/a", "nan", "null", "none"}
MARKETING_EXECUTIVE_TITLE = "Marketing Executive"
HR_EXECUTIVE_TITLE = "Human Resources Executive"

MALAY_FEMALE_PREFIXES = {
    "siti",
    "nur",
    "nurul",
    "nor",
    "noor",
    "puteri",
    "dayang",
    "sharifah",
    "farah",
    "sarah",
}
MALAY_MALE_PREFIXES = {
    "muhammad",
    "mohd",
    "ahmad",
    "syed",
    "tengku",
    "wan",
    "nik",
    "raja",
    "daniel",
    "john",
    "hafiz",
    "ali",
    "michael",
}
CHINESE_FEMALE_INDICATORS = {"mei", "ling", "hui", "ying", "yan", "ting", "pei", "linda", "jessica", "grace", "amanda", "emily"}
CHINESE_MALE_INDICATORS = {"wei", "ming", "jun", "hao", "peng", "jie", "zheng", "daniel", "chen", "kevin", "micheal", "david"}
INDIAN_FEMALE_INDICATORS = {"priya", "divya", "kavitha", "anjali", "lakshmi", "sangeetha"}
INDIAN_MALE_INDICATORS = {"raj", "kumar", "arjun", "vijay", "ravi", "krishna", "daniel"}


CANONICAL_COLUMN_ALIASES = {
    "Name": {"name", "employee name", "employee_name", "full name", "full_name"},
    "Age": {"age", "employee age", "umur"},
    "Performance_Rating": {
        "performance_rating",
        "performance rating",
        "rating",
        "performance score",
    },
    "Salary": {"salary", "gaji", "salary amount", "monthly salary", "income"},
    "Overtime_Hours": {
        "overtime_hours",
        "overtime hours",
        "ot hours",
        "overtime",
        "lembur",
    },
    "Hire_Date": {"hire_date", "hire date", "joining date", "start date", "tgl masuk"},
}

REQUIRED_HR_COLUMNS = [
    "Name",
    "Gender",
    "Salary",
    "Age",
    "Performance_Rating",
    "Overtime_Hours",
]


@dataclass
class CleaningStats:
    total_rows: int
    duplicates_removed: int = 0
    missing_values_fixed: int = 0
    negative_values_corrected: int = 0
    outliers_detected: int = 0
    gender_inferred_by_name: int = 0
    single_digit_ages_replaced: int = 0
    performance_rating_capped: int = 0
    salary_outliers_handled: int = 0

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)


def _normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def _normalize_column_key(name: str) -> str:
    normalized = name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def _resolve_column_name(df: pd.DataFrame, canonical_name: str) -> str | None:
    if canonical_name in df.columns:
        return canonical_name

    alias_pool = set()
    for alias in CANONICAL_COLUMN_ALIASES.get(canonical_name, set()):
        alias_pool.add(_normalize_column_key(alias))
    alias_pool.add(_normalize_column_key(canonical_name))

    for column in df.columns:
        if _normalize_column_key(str(column)) in alias_pool:
            return column

    return None


def _get_required_column_map(df: pd.DataFrame) -> Dict[str, str | None]:
    return {
        canonical: _resolve_column_name(df, canonical)
        for canonical in REQUIRED_HR_COLUMNS
    }


def validate_hr_schema(df: pd.DataFrame, strict_mode: bool = False) -> Dict[str, str | None]:
    required_map = _get_required_column_map(df)
    matched = [name for name, column in required_map.items() if column is not None]
    missing = [name for name, column in required_map.items() if column is None]

    if len(matched) < 4:
        raise ValueError(
            "This file does not look like an HR dataset. "
            "Need at least 4 core HR columns among: "
            "Name, Gender, Salary, Age, Performance Rating, Overtime Hours."
        )

    if strict_mode and missing:
        raise ValueError(
            "Strict mode: missing required HR columns: " + ", ".join(missing)
        )

    if strict_mode:
        high_missing_columns = []
        for canonical_name, resolved_column in required_map.items():
            if not resolved_column:
                continue
            missing_ratio = float(df[resolved_column].isna().mean())
            if missing_ratio > 0.40:
                high_missing_columns.append(f"{canonical_name} ({missing_ratio:.0%} missing)")

        if high_missing_columns:
            raise ValueError(
                "Strict mode: too many missing values in core HR columns: "
                + ", ".join(high_missing_columns)
            )

    return required_map


def _normalize_hr_label(value: str) -> str:
    """Fix 'Hr' and 'Human Resource' (without trailing s) after title-casing."""
    value = re.sub(r"\bHr\b", "Human Resources", value)
    value = re.sub(r"\bHuman Resource\b(?!s)", "Human Resources", value)
    value = re.sub(r"\bIt\b", "IT", value)
    return value


def _canonicalize_gender(value: Any) -> Any:
    normalized = _normalize_text(value)
    if normalized in MISSING_PLACEHOLDERS:
        return np.nan

    male_values = {
        "m",
        "male",
        "man",
        "lelaki",
        "laki",
        "boy",
    }
    female_values = {
        "f",
        "female",
        "woman",
        "perempuan",
        "girl",
        "femlae",
        "femle",
        "feamle",
        "fmale",
    }
    other_values = {"other", "o", "non-binary", "non binary", "nb"}

    if normalized in male_values:
        return "Male"
    if normalized in female_values:
        return "Female"
    if normalized in other_values:
        return "Other"

    return value


def infer_gender_from_malaysian_name(name: Any) -> Optional[str]:
    """Infer gender from Malaysian name patterns.

    Returns:
        "Male", "Female", or None when pattern is not detected.
    """
    if pd.isna(name):
        return None

    normalized_name = str(name).strip().lower()
    if not normalized_name:
        return None

    # Keep alpha-numeric and spaces only for robust token checks.
    cleaned_name = re.sub(r"[^a-z0-9\s]", " ", normalized_name)
    cleaned_name = re.sub(r"\s+", " ", cleaned_name).strip()
    if not cleaned_name:
        return None

    # Malay rule: prefix-based.
    first_token = cleaned_name.split(" ")[0]
    if first_token in MALAY_FEMALE_PREFIXES:
        return "Female"
    if first_token in MALAY_MALE_PREFIXES:
        return "Male"

    # Chinese and Indian rule: token indicator-based.
    tokens = set(cleaned_name.split(" "))

    if tokens & CHINESE_FEMALE_INDICATORS:
        return "Female"
    if tokens & CHINESE_MALE_INDICATORS:
        return "Male"

    if tokens & INDIAN_FEMALE_INDICATORS:
        return "Female"
    if tokens & INDIAN_MALE_INDICATORS:
        return "Male"

    return None


def auto_fill_missing_gender_by_name(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """Fill missing gender values using Malaysian name pattern rules."""
    adjusted_df = df.copy()
    inferred_count = 0
    name_column = _resolve_column_name(adjusted_df, "Name")
    if not name_column:
        return adjusted_df, inferred_count

    gender_columns = [
        column
        for column in adjusted_df.columns
        if "gender" in str(column).strip().lower()
    ]

    for gender_column in gender_columns:
        adjusted_df[gender_column] = adjusted_df[gender_column].astype("object")
        missing_gender_mask = adjusted_df[gender_column].isna()
        if not missing_gender_mask.any():
            continue

        inferred_gender = adjusted_df.loc[missing_gender_mask, name_column].apply(
            infer_gender_from_malaysian_name
        )
        inferred_count += int(inferred_gender.notna().sum())
        adjusted_df.loc[missing_gender_mask, gender_column] = inferred_gender

    return adjusted_df, inferred_count


def _canonicalize_job_title(value: Any) -> Any:
    if pd.isna(value):
        return value

    text = str(value).strip().lower()
    if text in MISSING_PLACEHOLDERS:
        return np.nan

    text = re.sub(r"\s+", " ", text)

    direct_map = {
        "marketing exec": MARKETING_EXECUTIVE_TITLE,
        "mktg exec": MARKETING_EXECUTIVE_TITLE,
        "hr exec": HR_EXECUTIVE_TITLE,
        "hr executive": HR_EXECUTIVE_TITLE,
        "human resource executive": HR_EXECUTIVE_TITLE,
        "human resources executive": HR_EXECUTIVE_TITLE,
    }
    if text in direct_map:
        return direct_map[text]

    tokens = []
    for token in text.split(" "):
        token_map = {
            "exec": "Executive",
            "asst": "Assistant",
            "mgr": "Manager",
            "sr": "Senior",
            "jr": "Junior",
            "hr": "Human Resources",
            "it": "IT",
            "ceo": "CEO",
            "cto": "CTO",
            "cfo": "CFO",
        }
        mapped = token_map.get(token)
        if mapped:
            tokens.append(mapped)
        else:
            tokens.append(token.title())

    collapsed = " ".join(tokens)
    collapsed = re.sub(r"Human Resources\s+Human Resources", "Human Resources", collapsed)
    collapsed = _normalize_hr_label(collapsed)
    return collapsed


def normalize_missing_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()

    object_columns = normalized_df.select_dtypes(include=["object", "category"]).columns
    for column in object_columns:
        normalized_df[column] = normalized_df[column].apply(
            lambda x: np.nan if _normalize_text(x) in MISSING_PLACEHOLDERS else x
        )

    return normalized_df


def standardize_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    standardized_df = df.copy()

    for column in standardized_df.select_dtypes(include=["object", "category"]).columns:
        normalized_column = column.lower()
        if "gender" in normalized_column:
            standardized_df[column] = standardized_df[column].apply(_canonicalize_gender)
        elif "job" in normalized_column and "title" in normalized_column:
            standardized_df[column] = standardized_df[column].apply(_canonicalize_job_title)
        else:
            standardized_df[column] = standardized_df[column].apply(
                lambda x: _normalize_hr_label(x.strip().title()) if isinstance(x, str) else x
            )

    return standardized_df


def fill_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    filled_df = df.copy()
    missing_before = int(filled_df.isna().sum().sum())

    filled_df, gender_inferred_count = auto_fill_missing_gender_by_name(filled_df)

    numeric_columns = filled_df.select_dtypes(include=[np.number]).columns
    for column in numeric_columns:
        median_value = filled_df[column].median()
        filled_df[column] = filled_df[column].fillna(median_value)

    categorical_columns = filled_df.select_dtypes(exclude=[np.number]).columns
    for column in categorical_columns:
        normalized_column = column.lower()
        if "gender" in normalized_column:
            # Keep as missing when no pattern is detected.
            continue
        else:
            mode_series = filled_df[column].mode(dropna=True)
            if not mode_series.empty:
                filled_df[column] = filled_df[column].fillna(mode_series.iloc[0])

    missing_after = int(filled_df.isna().sum().sum())
    fixed_count = missing_before - missing_after
    return filled_df, fixed_count, gender_inferred_count


def correct_negative_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    corrected_df = df.copy()
    corrected_count = 0

    for canonical_column in NEGATIVE_CHECK_COLUMNS:
        resolved_column = _resolve_column_name(corrected_df, canonical_column)
        if resolved_column and pd.api.types.is_numeric_dtype(corrected_df[resolved_column]):
            mask = corrected_df[resolved_column] < 0
            corrected_count += int(mask.sum())
            corrected_df.loc[mask, resolved_column] = corrected_df.loc[mask, resolved_column].abs()

    return corrected_df, corrected_count


def replace_single_digit_ages_with_median(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    adjusted_df = df.copy()
    age_column = _resolve_column_name(adjusted_df, "Age")
    if not age_column:
        return adjusted_df, 0

    numeric_age = pd.to_numeric(adjusted_df[age_column], errors="coerce")
    one_digit_mask = (numeric_age >= 0) & (numeric_age < 10)

    # Build median from realistic two-digit ages first.
    baseline_series = numeric_age[(numeric_age >= 10) & (numeric_age <= 99)].dropna()
    if baseline_series.empty:
        baseline_series = numeric_age[numeric_age >= 10].dropna()
    if baseline_series.empty:
        return adjusted_df, 0

    median_age = int(round(float(baseline_series.median()), 0))
    median_age = min(max(median_age, 10), 99)
    adjusted_df.loc[one_digit_mask, age_column] = median_age
    replaced_count = int(one_digit_mask.sum())

    return adjusted_df, replaced_count


def cap_performance_rating(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    capped_df = df.copy()
    rating_column = _resolve_column_name(capped_df, "Performance_Rating")
    if not rating_column:
        return capped_df, 0

    numeric_rating = pd.to_numeric(capped_df[rating_column], errors="coerce")
    capped_count = int((numeric_rating > 5).sum())
    capped_df[rating_column] = numeric_rating.clip(upper=5)
    return capped_df, capped_count


def standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    standardized_df = df.copy()

    for canonical_column in DATE_COLUMNS:
        resolved_column = _resolve_column_name(standardized_df, canonical_column)
        if resolved_column:
            series = standardized_df[resolved_column]
            parsed = pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=False)

            unresolved_mask = parsed.isna() & series.notna()
            if unresolved_mask.any():
                parsed_alt = pd.to_datetime(
                    series[unresolved_mask],
                    errors="coerce",
                    format="mixed",
                    dayfirst=True,
                )
                parsed.loc[unresolved_mask] = parsed_alt

            standardized_df[resolved_column] = parsed.dt.strftime("%Y-%m-%d")

    return standardized_df


def detect_and_cap_salary_outliers_iqr(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series, int]:
    """Replace only 6-figure salaries with median salary (integer, no decimals)."""
    capped_df = df.copy()
    salary_column = _resolve_column_name(capped_df, "Salary")
    if not salary_column or not pd.api.types.is_numeric_dtype(capped_df[salary_column]):
        return capped_df, pd.Series(False, index=df.index), 0

    numeric_salary = pd.to_numeric(capped_df[salary_column], errors="coerce")

    # Business rule: keep all 5-figure salaries; only handle 6-figure values.
    outlier_mask = numeric_salary >= 100000

    # Use median from non-6-figure salaries so replacements stay realistic.
    baseline_series = numeric_salary[(numeric_salary >= 0) & (numeric_salary < 100000)].dropna()
    if baseline_series.empty:
        baseline_series = numeric_salary[numeric_salary >= 0].dropna()

    if not baseline_series.empty:
        median_salary = int(round(float(baseline_series.median()), 0))
        capped_df.loc[outlier_mask, salary_column] = median_salary

    # Keep salary output clean for HR reporting: no fractional currency values.
    rounded_salary = pd.to_numeric(capped_df[salary_column], errors="coerce").round(0)
    capped_df[salary_column] = rounded_salary.astype("Int64")

    return capped_df, outlier_mask, int(outlier_mask.sum())


def enforce_integer_like_columns(df: pd.DataFrame) -> pd.DataFrame:
    enforced_df = df.copy()
    integer_columns = ["Age", "Performance_Rating", "Overtime_Hours"]

    for canonical_column in integer_columns:
        resolved_column = _resolve_column_name(enforced_df, canonical_column)
        if not resolved_column:
            continue

        numeric_series = pd.to_numeric(enforced_df[resolved_column], errors="coerce")
        enforced_df[resolved_column] = numeric_series.round(0).astype("Int64")

    return enforced_df


def clean_hr_data(
    df: pd.DataFrame,
    strict_mode: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, int], pd.DataFrame]:
    if df.empty:
        raise ValueError("Uploaded dataset is empty.")

    stats = CleaningStats(total_rows=len(df))
    working_df = normalize_missing_placeholders(df.copy())
    validate_hr_schema(working_df, strict_mode=strict_mode)

    before = len(working_df)
    working_df = working_df.drop_duplicates().reset_index(drop=True)
    stats.duplicates_removed = before - len(working_df)

    working_df = standardize_categorical_values(working_df)
    working_df = standardize_dates(working_df)
    working_df, stats.missing_values_fixed, stats.gender_inferred_by_name = fill_missing_values(working_df)
    working_df, stats.negative_values_corrected = correct_negative_values(working_df)
    working_df, stats.single_digit_ages_replaced = replace_single_digit_ages_with_median(working_df)
    working_df, stats.performance_rating_capped = cap_performance_rating(working_df)

    # Keep an original snapshot for reporting while applying fixes to cleaned output.
    pre_outlier_fix_df = working_df.copy()
    working_df, outlier_mask, stats.outliers_detected = detect_and_cap_salary_outliers_iqr(working_df)
    stats.salary_outliers_handled = stats.outliers_detected
    working_df = enforce_integer_like_columns(working_df)
    outliers_df = pre_outlier_fix_df.loc[outlier_mask].copy()

    return working_df, stats.to_dict(), outliers_df
