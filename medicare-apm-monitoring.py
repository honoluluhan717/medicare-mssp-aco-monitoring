"""MSSP 2024 ACO monitoring: descriptive financial summaries."""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

folder = Path(__file__).parent
out = folder / "output"
out.mkdir(exist_ok=True)

# Fail early if the source file or required CMS fields are unavailable.
source = folder / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"
if not source.is_file():
    raise FileNotFoundError(f"CMS input file not found: {source}")
required = {"ACO_ID", "ACO_Name", "BnchmkMinExp", "EarnSaveLoss",
            "Sav_rate", "QualScore", "Risk_Model", "Current_Track"}
df = pd.read_csv(source, low_memory=False)
missing_columns = required - set(df.columns)
if missing_columns:
    raise ValueError(f"Missing required CMS columns: {sorted(missing_columns)}")
if df["ACO_ID"].isna().any() or df["ACO_ID"].duplicated().any():
    raise ValueError("ACO_ID contains missing or duplicate values")
print("Rows and columns:", df.shape)
print("Duplicate ACO IDs:", df["ACO_ID"].duplicated().sum())
df.isna().sum().to_csv(out / "missing_data_report.csv", header=["Missing_Count"])

# Convert CMS financial fields to numbers.
numbers = ["BnchmkMinExp", "EarnSaveLoss", "Sav_rate", "QualScore"]
# Audit fields that could not be parsed as numbers.
numeric_fields = ["BnchmkMinExp", "EarnSaveLoss", "Sav_rate", "QualScore"]
numeric_audit = []
for col in numeric_fields:
    original_values = df[col].astype("string").str.strip()
    parsed = pd.to_numeric(
        original_values.str.replace(r"[$,%]", "", regex=True)
                       .str.replace(",", "", regex=False),
        errors="coerce"
    )
    invalid = original_values.notna() & ~original_values.isin(["", "-", "N/A"]) & parsed.isna()
    numeric_audit.append({"Field": col, "Non_numeric_values": int(invalid.sum()),
                          "Missing_after_conversion": int(parsed.isna().sum())})
    df[col] = parsed
pd.DataFrame(numeric_audit).to_csv(out / "numeric_conversion_audit.csv", index=False)

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
