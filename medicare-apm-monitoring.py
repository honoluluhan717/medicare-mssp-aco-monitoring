
"""
MEDICARE MSSP ACO PERFORMANCE MONITORING
CMS Performance Year 2024 Financial and Quality Results

Portfolio project using publicly available CMS data.
This is a descriptive analysis, not official CMS reconciliation.
"""

# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 2. DEFINE FILE PATHS
# ============================================================

# Location of this Python script
SCRIPT_DIR = Path(__file__).resolve().parent

# CMS CSV file in the same folder as this script
DATA_FILE = (
    SCRIPT_DIR
    / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"
)

# Folder for saving results
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. LOAD CMS DATA
# ============================================================

def load_data():

    print("\nLOADING CMS MSSP 2024 DATA")

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"CMS dataset not found:\n{DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE, low_memory=False)

    print("Number of ACO records:", len(df))
    print("Number of variables:", len(df.columns))

    return df


# ============================================================
# 4. DATA QUALITY CHECKS
# ============================================================

def inspect_data(df):

    print("\n=== DATA QUALITY CHECKS ===")

    print("Number of records:", len(df))
    print("Number of variables:", len(df.columns))

    required_columns = [
        "ACO_ID",
        "ACO_Name",
        "BnchmkMinExp",
        "EarnSaveLoss",
        "Sav_rate",
        "QualScore",
        "Risk_Model",
        "Current_Track"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns missing: {missing_columns}"
        )

    # Check duplicate ACO identifiers
    duplicate_count = df["ACO_ID"].duplicated().sum()

    print("Duplicate ACO IDs:", duplicate_count)

    if duplicate_count > 0:
        print("WARNING: Duplicate ACO IDs detected.")

    # Calculate missing data
    missing_report = pd.DataFrame({
        "Variable": df.columns,
        "Missing_Count": df.isna().sum().values,
        "Missing_Percent": df.isna().mean().values * 100
    })

    missing_report = missing_report.sort_values(
        "Missing_Percent",
        ascending=False
    )

    print("\nTop 10 variables with missing data:")
    print(missing_report.head(10).to_string(index=False))

    missing_report.to_csv(
        OUTPUT_DIR / "missing_data_report.csv",
        index=False
    )

    # Save variable dictionary
    dictionary = pd.DataFrame({
        "Variable": df.columns,
        "Data_Type": df.dtypes.astype(str).values
    })

    dictionary.to_csv(
        OUTPUT_DIR / "variable_dictionary.csv",
        index=False
    )


# ============================================================
# 5. CLEAN FINANCIAL VARIABLES
# ============================================================

def clean_financial_data(df):

    print("\n=== CLEANING FINANCIAL VARIABLES ===")

    df = df.copy()

    financial_vars = [
        "Sav_rate",
        "MinSavPerc",
        "BnchmkMinExp",
        "GenSaveLoss",
        "EarnSaveLoss",
        "FinalShareRate",
        "ABtotBnchmk",
        "ABtotExp",
        "QualScore"
    ]

    for col in financial_vars:

        if col in df.columns:

            cleaned = (
                df[col]
                .astype("string")
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.replace("%", "", regex=False)
                .str.strip()
            )

            cleaned = cleaned.replace({
                "": pd.NA,
                "-": pd.NA,
                "N/A": pd.NA
            })

            df[col] = pd.to_numeric(
                cleaned,
                errors="coerce"
            )

    print("Financial variables cleaned.")

    return df


# ============================================================
# 6. CLASSIFY ACO FINANCIAL PERFORMANCE
# ============================================================

def classify_financial_performance(df):

    print("\n=== FINANCIAL PERFORMANCE ===")

    df = df.copy()

    # Positive = benchmark exceeds expenditure
    # Negative = expenditure exceeds benchmark

    amount = df["BnchmkMinExp"]

    df["Financial_Status"] = np.select(
        [
            amount > 0,
            amount < 0,
            amount == 0
        ],
        [
            "Savings",
            "Losses",
            "Break-even"
        ],
        default="Missing"
    )

    print("\nACO counts by financial status:")

    print(
        df["Financial_Status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nTotal ACOs:", len(df))

    print(
        "Total benchmark-minus-expenditure:",
        df["BnchmkMinExp"].sum(min_count=1)
    )

    print(
        "Total earned savings / owed losses:",
        df["EarnSaveLoss"].sum(min_count=1)
    )

    return df


# ============================================================
# 7. FINANCIAL PERFORMANCE BY RISK MODEL
# ============================================================

def analyze_risk_models(df):

    print("\n=== PERFORMANCE BY RISK MODEL ===")

    summary = (
        df.groupby("Risk_Model", dropna=False)
        .agg(
            ACO_Count=("ACO_ID", "nunique"),
            Mean_Savings_Rate=("Sav_rate", "mean"),
            Median_Savings_Rate=("Sav_rate", "median"),
            Mean_Quality_Score=("QualScore", "mean"),
            Total_Gross_Savings_Losses=(
                "BnchmkMinExp", "sum"
            ),
            Total_Earned_Savings_Losses=(
                "EarnSaveLoss", "sum"
            )
        )
        .reset_index()
    )

    print(summary.to_string(index=False))

    summary.to_csv(
        OUTPUT_DIR / "financial_by_risk_model.csv",
        index=False
    )


# ============================================================
# 8. FINANCIAL PERFORMANCE BY TRACK
# ============================================================

def analyze_tracks(df):

    print("\n=== PERFORMANCE BY TRACK ===")

    summary = (
        df.groupby("Current_Track", dropna=False)
        .agg(
            ACO_Count=("ACO_ID", "nunique"),
            Mean_Savings_Rate=("Sav_rate", "mean"),
            Mean_Quality_Score=("QualScore", "mean"),
            Total_Gross_Savings_Losses=(
                "BnchmkMinExp", "sum"
            ),
            Total_Earned_Savings_Losses=(
                "EarnSaveLoss", "sum"
            )
        )
        .reset_index()
    )

    print(summary.to_string(index=False))

    summary.to_csv(
        OUTPUT_DIR / "financial_by_track.csv",
        index=False
    )


# ============================================================
# 9. IDENTIFY TOP AND BOTTOM 10 ACOS
# ============================================================

def rank_acos(df):

    print("\n=== TOP AND BOTTOM 10 ACOS ===")

    columns = [
        "ACO_ID",
        "ACO_Name",
        "BnchmkMinExp",
        "EarnSaveLoss",
        "QualScore"
    ]

    top_10 = df.nlargest(
        10, "BnchmkMinExp"
    )

    bottom_10 = df.nsmallest(
        10, "BnchmkMinExp"
    )

    print("\nTOP 10 BY GROSS SAVINGS")
    print(top_10[columns].to_string(index=False))

    print("\nBOTTOM 10 BY GROSS SAVINGS")
    print(bottom_10[columns].to_string(index=False))

    top_10[columns].to_csv(
        OUTPUT_DIR / "top_10_acos.csv",
        index=False
    )

    bottom_10[columns].to_csv(
        OUTPUT_DIR / "bottom_10_acos.csv",
        index=False
    )


# ============================================================
# 10. CREATE FINANCIAL PERFORMANCE CHART
# ============================================================

def create_chart(df):

    print("\n=== CREATING CHART ===")

    counts = (
        df["Financial_Status"]
        .value_counts()
        .reindex(
            ["Savings", "Losses", "Break-even", "Missing"],
            fill_value=0
        )
    )

    plt.figure(figsize=(9, 6))

    counts.plot(kind="bar")

    plt.title(
        "Medicare MSSP ACO Financial Performance, 2024"
    )

    plt.xlabel("Financial Performance")
    plt.ylabel("Number of ACOs")
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "financial_performance_distribution.png",
        dpi=300
    )

    plt.close()

    print("Chart saved successfully.")


# ============================================================
# 11. RUN ALL ANALYSES
# ============================================================

def main():

    print("=" * 60)
    print("MEDICARE MSSP ACO PERFORMANCE MONITORING")
    print("=" * 60)

    # Load data
    df = load_data()

    # Inspect data
    inspect_data(df)

    # Clean financial variables
    df = clean_financial_data(df)

    # Analyze financial performance
    df = classify_financial_performance(df)

    # Compare risk models
    analyze_risk_models(df)

    # Compare tracks
    analyze_tracks(df)

    # Rank ACOs
    rank_acos(df)

    # Create chart
    create_chart(df)

    print("\n" + "=" * 60)
    print("ALL ANALYSES COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("Results saved to:", OUTPUT_DIR)


# ============================================================
# 12. EXECUTE SCRIPT
# ============================================================

if __name__ == "__main__":
    main()
