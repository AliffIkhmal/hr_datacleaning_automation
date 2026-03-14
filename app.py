from __future__ import annotations

import streamlit as st
import pandas as pd

from hr_cleaning.cleaner import clean_hr_data
from hr_cleaning.report import generate_cleaning_report


st.set_page_config(page_title="Automated HR Data Cleaning", page_icon="🧹", layout="wide")
st.title("Automated HR Data Cleaning & Preprocessing System")
st.caption("Upload HR CSV data, run preprocessing, review report, and download cleaned output.")

uploaded_file = st.file_uploader("Upload HR dataset (CSV)", type=["csv"])
strict_mode = st.checkbox(
    "Strict HR-only mode (require all core columns and <= 40% missing in each core column)",
    value=False,
)

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Failed to read CSV file: {error}")
        st.stop()

    st.subheader("Dataset Preview")
    st.dataframe(raw_df.head(20), use_container_width=True)

    st.subheader("Detected Data Types")
    dtype_df = pd.DataFrame(
        {
            "Column": raw_df.columns,
            "Detected_Type": [str(raw_df[col].dtype) for col in raw_df.columns],
        }
    )
    st.dataframe(dtype_df, use_container_width=True)

    if st.button("Run Cleaning", type="primary"):
        try:
            cleaned_df, stats, outliers_df = clean_hr_data(raw_df, strict_mode=strict_mode)
            report_df = generate_cleaning_report(stats)
        except Exception as error:
            st.error(f"Cleaning failed: {error}")
            st.stop()

        st.success("Data cleaning completed successfully.")

        st.subheader("Cleaning Summary Report")
        st.dataframe(report_df, use_container_width=True)

        if not outliers_df.empty:
            st.subheader("Detected Salary Outliers (IQR)")
            st.dataframe(outliers_df, use_container_width=True)
        else:
            st.info("No salary outliers detected using IQR method.")

        st.subheader("Cleaned Dataset Preview")
        st.dataframe(cleaned_df.head(20), use_container_width=True)

        csv_data = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Cleaned CSV",
            data=csv_data,
            file_name="cleaned_hr_dataset.csv",
            mime="text/csv",
        )
else:
    st.info("Please upload a CSV file to begin.")
