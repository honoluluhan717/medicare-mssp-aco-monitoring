"""MSSP 2024 ACO monitoring: descriptive financial summaries."""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

folder = Path(__file__).parent
out = folder / "output"
out.mkdir(exist_ok=True)

df = pd.read_csv(folder / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv")
print("Rows and columns:", df.shape)
print("Duplicate ACO IDs:", df["ACO_ID"].duplicated().sum())
df.isna().sum().to_csv(out / "missing_data_report.csv", header=["Missing_Count"])

# Convert CMS financial fields to numbers.
numbers = ["BnchmkMinExp", "EarnSaveLoss", "Sav_rate", "QualScore"]
for col in numbers:
    df[col] = pd.to_numeric(
        df[col].astype("string").str.replace(r"[$,%]", "", regex=True),
        errors="coerce"
    )

# Positive benchmark difference means expenditures were below benchmark.
df["Financial_Status"] = "Missing"
df.loc[df["BnchmkMinExp"] > 0, "Financial_Status"] = "Savings"
df.loc[df["BnchmkMinExp"] < 0, "Financial_Status"] = "Losses"
df.loc[df["BnchmkMinExp"] == 0, "Financial_Status"] = "Break-even"

print("\nFinancial status:\n", df["Financial_Status"].value_counts())
print("Net benchmark difference:", df["BnchmkMinExp"].sum())
print("Net earned minus owed:", df["EarnSaveLoss"].sum())

# ACO-level means are unweighted; dollar amounts are totals.
for group in ["Risk_Model", "Current_Track"]:
    summary = df.groupby(group, dropna=False).agg(
        ACO_Count=("ACO_ID", "nunique"),
        Mean_Savings_Rate=("Sav_rate", "mean"),
        Mean_Quality_Score=("QualScore", "mean"),
        Net_Benchmark_Difference=("BnchmkMinExp", "sum"),
        Net_Earned_Minus_Owed=("EarnSaveLoss", "sum")
    )
    print("\n", group, "\n", summary)
    name = "financial_by_risk_model.csv" if group == "Risk_Model" else "financial_by_track.csv"
    summary.to_csv(out / name)

cols = ["ACO_ID", "ACO_Name", "BnchmkMinExp", "EarnSaveLoss", "QualScore"]
df.nlargest(10, "BnchmkMinExp")[cols].to_csv(out / "top_10_acos.csv", index=False)
df.nsmallest(10, "BnchmkMinExp")[cols].to_csv(out / "bottom_10_acos.csv", index=False)

df["Financial_Status"].value_counts().plot.bar(title="MSSP 2024: ACO Financial Performance")
plt.ylabel("Number of ACOs")
plt.tight_layout()
plt.savefig(out / "financial_performance_distribution.png")
plt.close()
print("\nSaved monitoring outputs to", out)
