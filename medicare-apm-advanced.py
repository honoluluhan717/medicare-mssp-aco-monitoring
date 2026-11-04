
"""
MEDICARE MSSP ACO ADVANCED PERFORMANCE MONITORING
Performance Year 2024

Expanded financial and quality monitoring using public CMS data.

This is a descriptive portfolio analysis, not an official
CMS financial reconciliation or causal evaluation.
"""

# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

from pathlib import Path
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ============================================================
# 2. DEFINE FILE PATHS AND VARIABLES
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent

# Separate output folder: does not overwrite original results
OUTPUT_DIR = SCRIPT_DIR / "output_advanced"

CSV_FILE = (
    SCRIPT_DIR
    / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"
)

REQUIRED_COLUMNS = [
    "ACO_ID",
    "ACO_Name",
    "Risk_Model",
    "Current_Track",
    "BnchmkMinExp",
    "EarnSaveLoss",
    "Sav_rate",
    "QualScore"
]

NUMERIC_COLUMNS = [
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


# ============================================================
# 3. LOAD AND VALIDATE CMS DATA
# ============================================================

def load_and_validate():

    print("\n=== LOADING CMS DATA ===")

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CMS data file not found:\n{CSV_FILE}"
        )

    df = pd.read_csv(CSV_FILE, low_memory=False)

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns missing: {missing_columns}"
        )

    if df["ACO_ID"].isna().any():
        raise ValueError("Missing ACO IDs detected.")

    if df["ACO_ID"].duplicated().any():
        raise ValueError("Duplicate ACO IDs detected.")

    print("Number of ACOs:", len(df))
    print("Number of variables:", len(df.columns))
    print("Duplicate ACO IDs: 0")

    return df


# ============================================================
# 4. CLEAN NUMERIC VARIABLES
# ============================================================

def clean_numbers(df):

    print("\n=== CLEANING NUMERIC VARIABLES ===")

    df = df.copy()

    for col in NUMERIC_COLUMNS:

        if col not in df.columns:
            continue

        cleaned = (
            df[col]
            .astype("string")
            .str.strip()
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace("%", "", regex=False)
        )

        cleaned = cleaned.replace({
            "": pd.NA,
            "-": pd.NA,
            "N/A": pd.NA,
            "nan": pd.NA
        })

        df[col] = pd.to_numeric(
            cleaned,
            errors="coerce"
        )

    print("Numeric variables cleaned.")

    return df


# ============================================================
# 5. DATA QUALITY MONITORING
# ============================================================

def data_quality_report(raw, df):

    print("\n=== DATA QUALITY REPORT ===")

    missing = pd.DataFrame({
        "Variable": df.columns,
        "Missing_Count": df.isna().sum().values,
        "Missing_Percent": (
            df.isna().mean().values * 100
        )
    })

    missing = missing.sort_values(
        "Missing_Percent",
        ascending=False
    )

    missing.to_csv(
        OUTPUT_DIR / "missing_data_report.csv",
        index=False
    )

    dictionary = pd.DataFrame({
        "Variable": raw.columns,
        "Original_Data_Type": raw.dtypes.astype(str).values,
        "Cleaned_Data_Type": df.dtypes.astype(str).values
    })

    dictionary.to_csv(
        OUTPUT_DIR / "variable_dictionary.csv",
        index=False
    )

    print(missing.head(10).to_string(index=False))


# ============================================================
# 6. CREATE FINANCIAL MONITORING INDICATORS
# ============================================================

def create_financial_indicators(df):

    print("\n=== CREATING FINANCIAL INDICATORS ===")

    df = df.copy()

    amount = df["BnchmkMinExp"]

    df["Financial_Status"] = np.select(
        [
            amount > 0,
            amount < 0,
            amount == 0
        ],
        [
            "Gross savings",
            "Gross losses",
            "Break-even"
        ],
        default="Missing"
    )

    earned = df["EarnSaveLoss"]

    df["Payment_Status"] = np.select(
        [
            earned > 0,
            earned < 0,
            earned == 0
        ],
        [
            "Positive earned amount",
            "Negative owed amount",
            "Zero"
        ],
        default="Missing"
    )

    # Exploratory MSR comparison.
    # This is NOT an official payment eligibility determination.

    if "MinSavPerc" in df.columns:

        df["Above_Reported_MSR"] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="boolean"
        )

        valid = (
            df["Sav_rate"].notna()
            & df["MinSavPerc"].notna()
        )

        df.loc[valid, "Above_Reported_MSR"] = (
            df.loc[valid, "Sav_rate"]
            > df.loc[valid, "MinSavPerc"]
        ).to_numpy()

    print("\nFinancial status:")
    print(df["Financial_Status"].value_counts())

    print("\nPayment status:")
    print(df["Payment_Status"].value_counts())

    return df


# ============================================================
# 7. SUMMARIZE PERFORMANCE BY GROUP
# ============================================================

def group_summary(df, group_variable):

    summary = (
        df.groupby(group_variable, dropna=False)
        .agg(
            ACO_Count=(
                "ACO_ID", "nunique"
            ),
            Mean_Savings_Rate=(
                "Sav_rate", "mean"
            ),
            Median_Savings_Rate=(
                "Sav_rate", "median"
            ),
            Mean_Quality_Score=(
                "QualScore", "mean"
            ),
            Median_Quality_Score=(
                "QualScore", "median"
            ),
            Gross_Savings_ACOs=(
                "Financial_Status",
                lambda x: (x == "Gross savings").sum()
            ),
            Gross_Loss_ACOs=(
                "Financial_Status",
                lambda x: (x == "Gross losses").sum()
            ),
            Net_Benchmark_Minus_Expenditure=(
                "BnchmkMinExp", "sum"
            ),
            Net_Earned_Minus_Owed=(
                "EarnSaveLoss", "sum"
            )
        )
        .reset_index()
    )

    return summary


# ============================================================
# 8. EXPORT FINANCIAL AND QUALITY TABLES
# ============================================================

def export_tables(df):

    print("\n=== EXPORTING MONITORING TABLES ===")

    columns = [
        "ACO_ID",
        "ACO_Name",
        "Risk_Model",
        "Current_Track",
        "BnchmkMinExp",
        "EarnSaveLoss",
        "Sav_rate",
        "QualScore",
        "Financial_Status",
        "Payment_Status"
    ]

    if "Above_Reported_MSR" in df.columns:
        columns.append("Above_Reported_MSR")

    # ACO-level monitoring dataset
    df[columns].to_csv(
        OUTPUT_DIR / "aco_monitoring_table.csv",
        index=False
    )

    # Risk model comparison
    risk_summary = group_summary(
        df, "Risk_Model"
    )

    risk_summary.to_csv(
        OUTPUT_DIR / "financial_by_risk_model.csv",
        index=False
    )

    print("\nRisk model comparison:")
    print(risk_summary.to_string(index=False))

    # Track comparison
    track_summary = group_summary(
        df, "Current_Track"
    )

    track_summary.to_csv(
        OUTPUT_DIR / "financial_by_track.csv",
        index=False
    )

    print("\nTrack comparison:")
    print(track_summary.to_string(index=False))

    # Financial rankings
    df.nlargest(
        10, "BnchmkMinExp"
    )[columns].to_csv(
        OUTPUT_DIR / "top_10_acos.csv",
        index=False
    )

    df.nsmallest(
        10, "BnchmkMinExp"
    )[columns].to_csv(
        OUTPUT_DIR / "bottom_10_acos.csv",
        index=False
    )

    # Quality rankings
    df.nlargest(
        10, "QualScore"
    )[columns].to_csv(
        OUTPUT_DIR / "top_10_quality_scores.csv",
        index=False
    )

    df.nsmallest(
        10, "QualScore"
    )[columns].to_csv(
        OUTPUT_DIR / "bottom_10_quality_scores.csv",
        index=False
    )

    # Descriptive correlations
    correlations = df[
        [
            "Sav_rate",
            "QualScore",
            "BnchmkMinExp",
            "EarnSaveLoss"
        ]
    ].corr()

    correlations.to_csv(
        OUTPUT_DIR / "descriptive_correlations.csv"
    )

    print("\nCorrelation matrix:")
    print(correlations.to_string())

    return correlations


# ============================================================
# 9. CREATE VISUALIZATIONS
# ============================================================

def create_charts(df):

    print("\n=== CREATING CHARTS ===")

    # Chart 1: Financial status distribution

    counts = (
        df["Financial_Status"]
        .value_counts()
        .reindex(
            [
                "Gross savings",
                "Gross losses",
                "Break-even",
                "Missing"
            ],
            fill_value=0
        )
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    counts.plot(kind="bar", ax=ax)

    ax.set_title(
        "MSSP 2024: ACO Financial Performance"
    )
    ax.set_xlabel("")
    ax.set_ylabel("Number of ACOs")
    ax.tick_params(axis="x", rotation=15)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "financial_performance_distribution.png",
        dpi=300
    )

    plt.close(fig)

    # Chart 2: Savings rate by risk model

    risk_means = (
        df.groupby("Risk_Model")["Sav_rate"]
        .mean()
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    risk_means.plot(kind="bar", ax=ax)

    ax.set_title(
        "Average Savings Rate by Risk Model"
    )
    ax.set_xlabel("")
    ax.set_ylabel("Mean Savings Rate (%)")
    ax.tick_params(axis="x", rotation=0)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "risk_model_comparison.png",
        dpi=300
    )

    plt.close(fig)

    # Chart 3: Savings rate by track

    track_means = (
        df.groupby("Current_Track")["Sav_rate"]
        .mean()
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    track_means.plot(kind="bar", ax=ax)

    ax.set_title(
        "Average Savings Rate by MSSP Track"
    )
    ax.set_xlabel("Track")
    ax.set_ylabel("Mean Savings Rate (%)")
    ax.tick_params(axis="x", rotation=0)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "track_comparison.png",
        dpi=300
    )

    plt.close(fig)

    # Chart 4: Quality score distribution

    fig, ax = plt.subplots(figsize=(9, 6))

    df["QualScore"].dropna().hist(
        bins=20,
        ax=ax
    )

    ax.set_title(
        "Distribution of ACO Quality Scores"
    )
    ax.set_xlabel("Quality Score")
    ax.set_ylabel("Number of ACOs")

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "quality_score_distribution.png",
        dpi=300
    )

    plt.close(fig)

    # Chart 5: Savings rate versus quality score

    paired = df[
        ["Sav_rate", "QualScore"]
    ].dropna()

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.scatter(
        paired["Sav_rate"],
        paired["QualScore"],
        alpha=0.5
    )

    ax.set_title(
        "ACO Savings Rate vs. Quality Score"
    )
    ax.set_xlabel("Savings Rate (%)")
    ax.set_ylabel("Quality Score")

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "savings_vs_quality.png",
        dpi=300
    )

    plt.close(fig)

    print("Five charts saved.")


# ============================================================
# 10. GENERATE AUTOMATED MONITORING REPORT
# ============================================================

def generate_report(df, correlations):

    print("\n=== GENERATING MONITORING REPORT ===")

    n_acos = len(df)

    savings_count = (
        df["Financial_Status"] == "Gross savings"
    ).sum()

    losses_count = (
        df["Financial_Status"] == "Gross losses"
    ).sum()

    net_benchmark = df[
        "BnchmkMinExp"
    ].sum(min_count=1)

    net_earned = df[
        "EarnSaveLoss"
    ].sum(min_count=1)

    mean_savings = df["Sav_rate"].mean()

    mean_quality = df["QualScore"].mean()

    correlation = correlations.loc[
        "Sav_rate", "QualScore"
    ]

    n_paired = len(
        df[["Sav_rate", "QualScore"]].dropna()
    )

    report = f"""
# Medicare MSSP ACO Performance Monitoring
## Performance Year 2024

### 1. Data Overview

- Source: CMS MSSP 2024 Financial and Quality Results
- Unit of analysis: Accountable Care Organization (ACO)
- Number of ACOs: {n_acos:,}

### 2. Financial Performance

- ACOs generating gross savings: {savings_count:,}
- ACOs generating gross losses: {losses_count:,}
- Net benchmark minus expenditures: ${net_benchmark:,.0f}
- Net earned savings minus owed losses: ${net_earned:,.0f}

These financial totals represent different measures.

### 3. Quality Performance

- Mean ACO quality score: {mean_quality:.2f}
- Mean ACO savings rate: {mean_savings:.2f}%

Both are unweighted averages across ACOs.

### 4. Savings and Quality Relationship

- Pearson correlation: {correlation:.3f}
- ACOs with complete savings and quality data: {n_paired}

This correlation is descriptive and does not establish causation.

### 5. Interpretation and Limitations

1. Cross-sectional descriptive analysis.
2. Group comparisons are not causal estimates.
3. ACOs differ in size and beneficiary characteristics.
4. Raw dollar rankings are not efficiency rankings.
5. Quality scores are not independently risk-adjusted here.
6. The exploratory MSR indicator is not official payment eligibility.
7. Financial reconciliation involves additional CMS program rules.
8. Missing values may reflect CMS reporting requirements.

### 6. Output

The output_advanced folder contains:

- ACO-level monitoring table
- Financial summaries by risk model and track
- Top and bottom financial rankings
- Top and bottom quality rankings
- Descriptive correlation matrix
- Data quality reports
- Five charts

### 7. Conclusion

This project demonstrates a reproducible approach to
monitoring Medicare ACO financial and quality performance
using publicly available CMS data.

The analysis supports descriptive performance assessment,
identification of variation, and further investigation.
"""

    report_path = (
        OUTPUT_DIR / "monitoring_report.md"
    )

    report_path.write_text(
        report.strip(),
        encoding="utf-8"
    )

    print("Monitoring report saved.")


# ============================================================
# 11. MAIN ANALYSIS PIPELINE
# ============================================================

def main():

    print("=" * 60)
    print("MEDICARE MSSP ADVANCED PERFORMANCE MONITORING")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Load CMS data
    raw = load_and_validate()

    # Clean numeric variables
    df = clean_numbers(raw)

    # Export data quality reports
    data_quality_report(raw, df)

    # Create financial indicators
    df = create_financial_indicators(df)

    # Export financial and quality summaries
    correlations = export_tables(df)

    # Generate charts
    create_charts(df)

    # Generate Markdown report
    generate_report(df, correlations)

    print("\n" + "=" * 60)
    print("ADVANCED ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("Results saved to:")
    print(OUTPUT_DIR)


# ============================================================
# 12. EXECUTE THE SCRIPT
# ============================================================

if __name__ == "__main__":
    main()
