# ACO Performance Risk Screening

A small follow-up analysis using the 2024 CMS Medicare Shared Savings Program (MSSP) ACO-level financial and quality results.

## Question

Which ACOs have financial or quality performance patterns that warrant a closer look?

## Screening rules

- **Financial flag:** `BnchmkMinExp < 0` (expenditures exceed benchmark).
- **Quality flag:** `QualScore` at or below the 25th percentile of nonmissing ACO quality scores in this dataset.
- **Priority review:** Both flags.
- **Review:** Either flag, but not both.
- **No flag:** Neither flag.
- **Not assessed:** Missing financial or quality measure.

These are exploratory rules, **not CMS monitoring thresholds or evidence of misconduct**. A flag identifies an ACO for follow-up, not a conclusion about performance or compliance. A single-year dataset cannot identify deteriorating trends.

## Run

Place the CMS CSV beside the original Python scripts in the repository root:

```text
PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv
```

From the repository root:

```bash
pip install pandas matplotlib
python risk-screening/risk_screening.py
```

The script writes `risk-screening/results/aco_risk_flags.csv` and `risk-screening/results/risk_flag_counts.png`.

## Interpretation

Review flagged ACOs against prior-year results, population and organizational characteristics, and relevant quality measures before drawing conclusions. The rules do not adjust for case mix, ACO size, or differences in model participation.
