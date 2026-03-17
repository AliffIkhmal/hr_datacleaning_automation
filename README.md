# Data Automation Toolkit

## Architecture

```text
HRdata_cleaning/
├─ app.py                          # Streamlit UI
├─ requirements.txt
├─ core/
│  ├─ cleaner_router.py            # Tool registry & dispatch
│  ├─ industry_schemas.py          # Column definitions & alias pools
│  ├─ report_generator.py          # Cleaning report builder
│  └─ schema_detector.py           # Industry detection & column resolution
├─ tools/
│  ├─ base.py                      # BaseCleaner ABC & CleaningResult
│  ├─ cleaning_utils.py            # Shared cleaning utilities
│  ├─ hr_cleaning/
│  │  ├─ cleaner.py                # Core HR cleaning pipeline
│  │  ├─ hr_cleaner.py             # BaseCleaner adapter
│  │  ├─ report.py                 # HR report generator
│  │  └─ HR_raw_data.csv           # Sample HR dataset
│  ├─ sales/
│  │  ├─ sales_cleaner.py
│  │  └─ sales_messy_dataset.csv
│  ├─ manufacturing/
│  │  ├─ manufacturing_cleaner.py
│  │  └─ manufacturing_messy_dataset.csv
│  ├─ logistics/
│  │  ├─ logistics_cleaner.py
│  │  └─ logistics_messy_dataset.csv
│  └─ ecommerce/
│     ├─ ecommerce_cleaner.py
│     └─ ecommerce_messy_dataset.csv
└─ tests/
   ├─ test_cleaner.py              # HR pipeline tests
   └─ test_toolkit_modules.py      # Toolkit-wide tests
```

## Flow

1. User selects an industry cleaner in the Streamlit UI.
2. User uploads a CSV dataset.
3. The schema detector classifies numeric, categorical, date-like, and identifier columns and detects the industry.
4. Column-name pattern matching generates suggested cleaning rules.
5. A column mapping table shows which schema fields were matched in the uploaded file.
6. A pre-cleaning quality summary shows missing-value counts and negative values per column.
7. The cleaner router dispatches the dataset to the selected cleaner.
8. The cleaner returns a cleaned dataset and a cleaning report.
9. A column-level changes table shows exactly which columns were modified.
10. The UI renders the preview, report, and download action.

## HR Integration

The HR cleaner is built around a dedicated Malaysian HR pipeline:

- `tools/hr_cleaning/hr_cleaner.py` — `BaseCleaner` adapter that calls the HR pipeline
- `tools/hr_cleaning/cleaner.py` — full HR cleaning logic (deduplication, salary outlier removal, date standardisation, gender inference from Malaysian name patterns for missing values, job title canonicalisation)
- `tools/hr_cleaning/report.py` — HR-specific report generator

## Cleaning Utilities (`tools/cleaning_utils.py`)

| Function | Purpose |
|---|---|
| `normalize_missing_placeholders` | Converts `""`, `"na"`, `"null"`, etc. to `NaN` |
| `remove_duplicates` | Drops duplicate rows |
| `correct_negatives` | Converts negative values to their absolute value |
| `standardize_dates` | Parses mixed date formats → `YYYY-MM-DD` |
| `cap_outliers_iqr` | Caps outliers using IQR method (skips columns with < 10 rows) |
| `validate_ranges` | Clips numeric columns to defined `[min, max]` bounds |
| `standardize_categoricals` | Title-cases text while preserving all-caps acronyms (e.g. `HR`, `IT`) |
| `fill_missing` | Fills missing numerics with median, categoricals with mode (skips identifier columns) |
| `round_numeric_columns` | Rounds all numeric columns to 0 decimal places |

## Run Locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit app:

   ```bash
   streamlit run app.py
   ```

3. Run tests:

   ```bash
   python -m pytest tests/ -v
   ```

## Current Status

- HR Data Cleaner: implemented and integrated
- Sales Data Cleaner: scaffolded placeholder
- Manufacturing Data Cleaner: scaffolded placeholder
- Logistics Data Cleaner: scaffolded placeholder
- E-commerce Data Cleaner: scaffolded placeholder
