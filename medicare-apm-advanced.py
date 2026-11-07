"""MSSP 2024 ACO monitoring: risk, quality, and correlations."""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

folder = Path(__file__).parent
out = folder / "output_advanced"
out.mkdir(exist_ok=True)

df = pd.read_csv(folder / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv")
print("Rows and columns:", df.shape)
print("Duplicate ACO IDs:", df["ACO_ID"].duplicated().sum())

for col in ["BnchmkMinExp", "EarnSaveLoss", "Sav_rate", "QualScore"]:
    df[col] = pd.to_numeric(
        df[col].astype("string").str.replace(r"[$,%]", "", regex=True),
        errors="coerce"
    )

df["Financial_Status"] = "Missing"
df.loc[df["BnchmkMinExp"] > 0, "Financial_Status"] = "Gross savings"
df.loc[df["BnchmkMinExp"] < 0, "Financial_Status"] = "Gross losses"
df.loc[df["BnchmkMinExp"] == 0, "Financial_Status"] = "Break-even"

df["Payment_Status"] = "Missing"
df.loc[df["EarnSaveLoss"] > 0, "Payment_Status"] = "Positive earned amount"
df.loc[df["EarnSaveLoss"] < 0, "Payment_Status"] = "Negative owed amount"
df.loc[df["EarnSaveLoss"] == 0, "Payment_Status"] = "Zero"

df.isna().sum().to_csv(out / "missing_data_report.csv", header=["Missing_Count"])
df.to_csv(out / "aco_monitoring_table.csv", index=False)

for group in ["Risk_Model", "Current_Track"]:
    summary = df.groupby(group, dropna=False).agg(
        ACO_Count=("ACO_ID", "nunique"),
        Mean_Savings_Rate=("Sav_rate", "mean"),
        Median_Savings_Rate=("Sav_rate", "median"),
        Mean_Quality_Score=("QualScore", "mean"),
        Net_Benchmark_Difference=("BnchmkMinExp", "sum"),
        Net_Earned_Minus_Owed=("EarnSaveLoss", "sum")
    )
    name = "financial_by_risk_model.csv" if group == "Risk_Model" else "financial_by_track.csv"
    summary.to_csv(out / name)
    print("\n", group, "\n", summary)

cols = ["ACO_ID", "ACO_Name", "BnchmkMinExp", "EarnSaveLoss", "QualScore"]
for measure, label in [("BnchmkMinExp", "acos"), ("QualScore", "quality_scores")]:
    df.nlargest(10, measure)[cols].to_csv(out / f"top_10_{label}.csv", index=False)
    df.nsmallest(10, measure)[cols].to_csv(out / f"bottom_10_{label}.csv", index=False)

corr = df[["Sav_rate", "QualScore", "BnchmkMinExp", "EarnSaveLoss"]].corr()
corr.to_csv(out / "descriptive_correlations.csv")
print("\nCorrelation matrix:\n", corr)

# Five charts, saved individually.
df["Financial_Status"].value_counts().plot.bar(title="ACO Financial Performance")
plt.tight_layout()
plt.savefig(out / "financial_performance_distribution.png")
plt.close()

for group, filename in [("Risk_Model", "risk_model_comparison.png"),
                        ("Current_Track", "track_comparison.png")]:
    df.groupby(group)["Sav_rate"].mean().plot.bar(title=f"Mean Savings Rate by {group}")
    plt.ylabel("Mean savings rate (%)")
    plt.tight_layout()
    plt.savefig(out / filename)
    plt.close()

df["QualScore"].dropna().hist(bins=20)
plt.title("ACO Quality Score Distribution")
plt.xlabel("Quality score")
plt.tight_layout()
plt.savefig(out / "quality_score_distribution.png")
plt.close()

df.plot.scatter(x="Sav_rate", y="QualScore", alpha=0.5,
                title="Savings Rate vs. Quality Score")
plt.tight_layout()
plt.savefig(out / "savings_vs_quality.png")
plt.close()

print("\nACOs:", len(df))
print("Net benchmark difference:", df["BnchmkMinExp"].sum())
print("Net earned minus owed:", df["EarnSaveLoss"].sum())
print("Saved advanced outputs to", out)
