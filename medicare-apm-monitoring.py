
"""
MEDICARE MSSP ACO PERFORMANCE MONITORING
CMS Performance Year 2024 Financial and Quality Results

Descriptive analysis of CMS PY2024 ACO financial and quality results.
"""

# import libraries

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# define file paths
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = (
    SCRIPT_DIR
    / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"
)
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# load cms data

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


# data quality checks

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
    duplicate_count = df["ACO_ID"].duplicated().sum()

    print("Duplicate ACO IDs:", duplicate_count)

    if duplicate_count > 0:
        print("WARNING: Duplicate ACO IDs detected.")
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
    dictionary = pd.DataFrame({
        "Variable": df.columns,
        "Data_Type": df.dtypes.astype(str).values
    })

    dictionary.to_csv(
        OUTPUT_DIR / "variable_dictionary.csv",
        index=False
    )


# clean financial variables

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


# classify aco financial performance

def classify_financial_performance(df):

    print("\n=== FINANCIAL PERFORMANCE ===")

    df = df.copy()

    # Positive values indicate spending below the benchmark.

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


# financial performance by risk model

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


# financial performance by track

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


# identify top and bottom 10 acos

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


# create financial performance chart

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


# run all analyses

def main():

    print("=" * 60)
    print("MEDICARE MSSP ACO PERFORMANCE MONITORING")
    print("=" * 60)
    df = load_data()
    inspect_data(df)
    df = clean_financial_data(df)
    df = classify_financial_performance(df)
    analyze_risk_models(df)
    analyze_tracks(df)
    rank_acos(df)
    create_chart(df)

    print("\n" + "=" * 60)
    print("ALL ANALYSES COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("Results saved to:", OUTPUT_DIR)


# execute script

if __name__ == "__main__":
    main()
