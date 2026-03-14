# Automated HR Data Cleaning & Preprocessing System

## Suggested Project Structure

```text
HRdata_cleaning/
├─ app.py
├─ requirements.txt
├─ README.md
└─ hr_cleaning/
   ├─ __init__.py
   ├─ cleaner.py
   └─ report.py
```

## Basic Architecture Diagram (Explanation)

```text
[User]
   │ Upload CSV / Click "Run Cleaning"
   ▼
[Streamlit UI: app.py]
   │
   ├─ Reads CSV with pandas
   ├─ Shows preview + detected dtypes
   ├─ Calls cleaning service
   ▼
[Data Cleaning Module: cleaner.py]
   │
   ├─ Remove duplicates
   ├─ Fill missing values (median/mode)
   ├─ Correct negatives (Age, Salary, Overtime_Hours)
   ├─ Standardize categorical values
   ├─ Convert Hire_Date to YYYY-MM-DD
   └─ Detect Salary outliers (IQR)
   │
   ▼
[Reporting Module: report.py]
   └─ Builds summary metrics table
   │
   ▼
[Streamlit UI: app.py]
   ├─ Displays cleaning report
   ├─ Displays outlier rows
   └─ Provides cleaned CSV download
```

## Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start app:
   ```bash
   streamlit run app.py
   ```
