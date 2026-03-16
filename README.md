# Data Automation Toolkit

## Architecture

```text
HRdata_cleaning/
├─ app.py
├─ core/
│  ├─ cleaner_router.py
│  ├─ report_generator.py
│  └─ schema_detector.py
├─ tools/
│  ├─ hr/
│  │  └─ hr_cleaner.py
│  ├─ sales/
│  │  └─ sales_cleaner.py
│  ├─ manufacturing/
│  │  └─ manufacturing_cleaner.py
│  ├─ logistics/
│  │  └─ logistics_cleaner.py
│  └─ ecommerce/
│     └─ ecommerce_cleaner.py
├─ hr_cleaning/
│  ├─ cleaner.py
│  └─ report.py
├─ outputs/
├─ data/
└─ tests/
```

## Flow

1. User selects an industry cleaner in the Streamlit UI.
2. User uploads a CSV dataset.
3. The schema detector classifies numeric, categorical, date-like, and identifier columns.
4. Column-name pattern matching generates suggested cleaning rules.
5. The cleaner router dispatches the dataset to the selected cleaner.
6. The cleaner returns a cleaned dataset and a cleaning report.
7. The UI renders the preview, report, and download action.

## Existing HR Integration

The HR tool is implemented as an adapter around the existing HR pipeline:

- `tools/hr/hr_cleaner.py` calls `hr_cleaning.cleaner.clean_hr_data`
- `hr_cleaning/report.py` still builds the HR report
- This keeps the current HR cleaning behavior intact while exposing it through the modular toolkit

## Run Locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit app:

   ```bash
   streamlit run app.py
   ```

## Current Status

- HR Data Cleaner: implemented and integrated
- Sales Data Cleaner: implemented and integrated
- Manufacturing Data Cleaner: scaffolded placeholder
- Logistics Data Cleaner: scaffolded placeholder
- E-commerce Data Cleaner: scaffolded placeholder
