# Medicare MSSP ACO Performance Monitoring | 2024

**Python portfolio project | Medicare Shared Savings Program (MSSP) | Financial and quality performance**

This project analyzes publicly reported **2024 Medicare Shared Savings Program (MSSP)** results for **476 Accountable Care Organizations (ACOs)**. It demonstrates a reproducible approach to data validation, financial and quality performance monitoring, ACO comparisons, and reporting using Python.

The analysis is **descriptive**. It is not an official CMS reconciliation, a causal evaluation, or an assessment of a CMMI demonstration model.

## Key findings

| Metric | 2024 result |
|---|---:|
| ACOs analyzed | 476 |
| ACOs with gross savings relative to benchmark | 422 (88.7%) |
| ACOs with gross losses relative to benchmark | 54 (11.3%) |
| Net benchmark-minus-expenditure amount | $6.61 billion |
| Net reported earned savings minus owed losses | $4.12 billion |
| ACOs with positive earned amounts | 360 |
| ACOs with negative owed amounts | 16 |
| ACOs with zero earned/owed amounts | 100 |
| Correlation: savings rate vs. quality score | 0.157 |

**Interpretation:** Most ACOs had expenditures below their benchmarks, but gross savings do not translate dollar-for-dollar into earned shared-savings payments. The association between savings rate and quality score was weak and positive; it should not be interpreted causally.

### Comparison by financial risk model

| Measure | One-sided risk | Two-sided risk |
|---|---:|---:|
| Number of ACOs | 157 | 319 |
| Mean savings rate | 3.20% | 5.53% |
| Mean quality score | 78.44 | 83.60 |
| ACOs with gross savings | 130 | 292 |

These are **unweighted, descriptive comparisons**. Risk-model groups can differ in size, beneficiary populations, organizational experience, and other characteristics.

## Visualizations

### Financial performance distribution

![ACO financial performance distribution](output_advanced/financial_performance_distribution.png)

### Average savings rate by risk model

![Average savings rate by risk model](output_advanced/risk_model_comparison.png)

### Average savings rate by MSSP track

![Average savings rate by MSSP track](output_advanced/track_comparison.png)

### Quality score distribution

![Distribution of ACO quality scores](output_advanced/quality_score_distribution.png)

### Savings rate and quality score

![Scatterplot of ACO savings rate and quality score](output_advanced/savings_vs_quality.png)

> **Note:** Images will display on GitHub after the five PNG files are committed under `output_advanced/`.

## Methods

1. **Import and validate:** Read the CMS ACO-level CSV, verify required variables, and check for duplicate ACO IDs.
2. **Clean variables:** Convert selected financial and quality fields to numeric types and summarize missingness.
3. **Classify financial results:** Categorize ACOs using the sign of benchmark-minus-expenditure amounts, and separately classify reported earned/owed amounts.
4. **Compare ACO groups:** Summarize savings rates, quality scores, and financial totals by `Risk_Model` and `Current_Track`.
5. **Monitor quality and financial relationships:** Generate score distributions, a savings-versus-quality scatterplot, and descriptive Pearson correlations.
6. **Export reports:** Save ACO-level monitoring data, comparison tables, rankings, charts, and a Markdown report.

The exploratory comparison of `Sav_rate` and `MinSavPerc` in the advanced script is **not an official shared-savings eligibility determination**.

## Repository contents

```text
medicare-mssp-aco-monitoring/
├── medicare-apm-monitoring.py      # Initial financial monitoring analysis
├── medicare-apm-advanced.py        # Expanded financial and quality analysis
├── output_advanced/               # Generated charts and selected reports
│   ├── financial_performance_distribution.png
│   ├── risk_model_comparison.png
│   ├── track_comparison.png
│   ├── quality_score_distribution.png
│   ├── savings_vs_quality.png
│   └── monitoring_report.md
└── README.md
```

## Data source

**Centers for Medicare & Medicaid Services (CMS):** Medicare Shared Savings Program, Performance Year 2024 ACO Financial and Quality Results.

The scripts expect the CMS CSV file to be in the same directory as the Python scripts, with this filename:

```text
PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv
```

The source dataset is not required to be committed to this repository. Obtain the public-use data from CMS and place it locally alongside the scripts.

## How to run

**Requirements:** Python 3 and the following packages:

```bash
pip install pandas numpy matplotlib
```

Run the original analysis:

```bash
python medicare-apm-monitoring.py
```

Run the expanded analysis:

```bash
python medicare-apm-advanced.py
```

On Windows, `py` may be used instead of `python`.

The original script saves files to `output/`; the expanded script saves files to `output_advanced/`. Both folders are created automatically.

## Selected outputs

- [ACO-level monitoring table](output_advanced/aco_monitoring_table.csv)
- [Financial results by risk model](output_advanced/financial_by_risk_model.csv)
- [Financial results by track](output_advanced/financial_by_track.csv)
- [Descriptive correlation matrix](output_advanced/descriptive_correlations.csv)
- [Automated monitoring report](output_advanced/monitoring_report.md)

These links work after the corresponding generated files have been pushed to GitHub.

## Limitations

- This is a **single-year, cross-sectional** analysis; it does not establish causal effects.
- Group averages are **unweighted** and do not adjust for beneficiary mix, ACO size, or other confounding factors.
- Dollar-denominated savings rankings can reflect organizational size and should not be treated as efficiency rankings.
- The analysis uses reported quality scores and does not independently reproduce CMS quality scoring.
- MSSP payment reconciliation involves thresholds, sharing rates, quality requirements, caps, and other program-specific rules; the script does not reconstruct the full official calculation.
- Missing values may reflect reporting applicability rather than data errors.

## Project purpose

This project illustrates practical workflows relevant to **Medicare value-based payment analytics, healthcare program performance monitoring, data quality assessment, and reproducible reporting**.
