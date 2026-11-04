"""Screen 2024 MSSP ACOs for financial and quality performance concerns."""

from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"
OUTPUT = Path(__file__).resolve().parent / "results"


def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Place the CMS CSV next to your original scripts: {DATA}")

    df = pd.read_csv(DATA, low_memory=False)
    required = ["ACO_ID", "ACO_Name", "BnchmkMinExp", "Sav_rate", "QualScore"]
    missing = [name for name in required if name not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df["ACO_ID"].isna().any() or df["ACO_ID"].duplicated().any():
        raise ValueError("ACO_ID must be present and unique.")

    for name in ["BnchmkMinExp", "Sav_rate", "QualScore"]:
        df[name] = pd.to_numeric(
            df[name].astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip(),
            errors="coerce",
        )

    # Lower quartile of reported quality scores, among nonmissing observations.
    quality_cutoff = df["QualScore"].quantile(0.25)
    df["Financial_Flag"] = df["BnchmkMinExp"] < 0
    df["Quality_Flag"] = df["QualScore"] <= quality_cutoff

    # Do not classify records without both measures.
    complete = df[["BnchmkMinExp", "QualScore"]].notna().all(axis=1)
    df["Review_Priority"] = "Not assessed"
    df.loc[complete, "Review_Priority"] = "No flag"
    df.loc[complete & (df["Financial_Flag"] | df["Quality_Flag"]), "Review_Priority"] = "Review"
    df.loc[complete & df["Financial_Flag"] & df["Quality_Flag"], "Review_Priority"] = "Priority review"

    OUTPUT.mkdir(parents=True, exist_ok=True)
    cols = required + ["Financial_Flag", "Quality_Flag", "Review_Priority"]
    df[cols].sort_values(
        "Review_Priority",
        key=lambda s: s.map({
            "Priority review": 0, "Review": 1, "No flag": 2, "Not assessed": 3
        }),
    ).to_csv(OUTPUT / "aco_risk_flags.csv", index=False)

    counts = df["Review_Priority"].value_counts().reindex(
        ["Priority review", "Review", "No flag", "Not assessed"], fill_value=0
    )
    ax = counts.plot.bar(figsize=(8, 5), color="steelblue")
    ax.set_title("2024 MSSP ACOs: Performance Review Flags")
    ax.set_xlabel("")
    ax.set_ylabel("Number of ACOs")
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(OUTPUT / "risk_flag_counts.png", dpi=200)
    plt.close()

    print(f"ACOs: {len(df)}")
    print(f"Quality cutoff (25th percentile): {quality_cutoff:.2f}")
    print(counts.to_string())
    print(f"Saved results to: {OUTPUT}")


if __name__ == "__main__":
    main()
