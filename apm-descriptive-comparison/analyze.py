"""Descriptive comparison using CMS-published APM summary statistics."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"

def load(name):
    df = pd.read_csv(ROOT / "data" / name, keep_default_na=False)
    if not df.source_url.str.startswith("https://").all():
        raise ValueError(f"Missing source URL: {name}")
    return df

def plot_bar(df, x, y, title, ylabel, filename):
    ax = df.plot.bar(x=x, y=y, legend=False, figsize=(8, 4))
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel("Period")
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=180)
    plt.close()

def main():
    OUT.mkdir(exist_ok=True)
    part = load("participation.csv")
    fin = load("financial_indicators.csv")
    qual = load("quality_indicators.csv")
    design = load("model_design.csv")
    fin["value"] = pd.to_numeric(fin["value"], errors="raise")
    qual["numeric_value"] = pd.to_numeric(qual["value"], errors="coerce")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, df, title in [
        (axes[0], part[(part.model == "MSSP") & (part.basis == "Jan 1 snapshot")], "MSSP snapshots"),
        (axes[1], part[part.model == "ACO REACH / GPDC"], "GPDC / ACO REACH")
    ]:
        ax.plot(df.year, df.participant_count, marker="o")
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel("ACOs")
        ax.tick_params(axis="x", rotation=35)
    plt.tight_layout()
    plt.savefig(OUT / "participation_trends.png", dpi=180)
    plt.close()
    plot_bar(fin[(fin.model == "MSSP") & (fin.measure == "benchmark_net_savings_per_beneficiary")],
             "period", "value", "MSSP: net savings per beneficiary", "USD per beneficiary", "mssp_per_capita.png")
    plot_bar(fin[(fin.model == "ACO REACH") & (fin.measure == "cms_benchmark_net_savings")],
             "period", "value", "GPDC / REACH: savings relative to benchmark", "USD millions", "reach_benchmark_savings.png")
    plot_bar(fin[fin.model == "BPCI Advanced"],
             "period", "value", "BPCI Advanced: published evaluation net savings", "USD millions", "bpci_evaluation_savings.png")
    plot_bar(qual[(qual.model == "ACO REACH") & (qual.measure == "timely_followup_standard_new_entrant")],
             "period", "numeric_value", "REACH: timely follow-up", "Percent", "reach_quality_trend.png")
    for df, name in [(part, "participation"), (fin, "financial"), (qual, "quality"), (design, "design")]:
        df.to_csv(OUT / f"{name}_with_sources.csv", index=False)
    print("Created five figures and four source-linked tables.")
    print("Do not compare raw financial or quality totals across models.")

if __name__ == "__main__":
    main()
