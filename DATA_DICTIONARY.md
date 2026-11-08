# Data dictionary — MSSP performance year 2024

This is a short guide to the fields used in this repository, **not** a replacement for the official CMS data dictionary.

**Official documentation:** [CMS Performance Year 2024 Financial and Quality Results data dictionary (PDF)](https://data.cms.gov/sites/default/files/2025-08/Data_Dictionary-Medicare_Shared_Savings_Program-Performance_Year_Financial_and_Quality_Results_2024-508.pdf). If this PDF link changes, find the documentation through the [CMS MSSP dataset page](https://data.cms.gov/medicare-shared-savings-program/performance-year-financial-and-quality-results).

| CSV field | Plain-language description | Used for |
| --- | --- | --- |
| `ACO_ID` | Identifier for each accountable care organization | Unique record checks |
| `ACO_Name` | Name of the ACO | Ranking tables |
| `Current_Track` | MSSP participation track | Track comparisons |
| `Risk_Model` | One-sided or two-sided **financial** risk arrangement | Risk-arrangement comparisons |
| `BnchmkMinExp` | Benchmark minus expenditures; positive values indicate spending below the benchmark | Gross benchmark savings/losses |
| `EarnSaveLoss` | Final earned shared savings or owed shared losses, as reported by CMS | Financial payment outcome |
| `Sav_rate` | CMS-reported savings rate, expressed in percentage points | Comparisons and plots |
| `QualScore` | CMS-reported overall quality score | Quality summaries and plots |

## Reading the results

- `BnchmkMinExp` and `EarnSaveLoss` are **not interchangeable**. An ACO's gross benchmark difference is not necessarily the amount it earns or owes.
- `Risk_Model` concerns **financial risk**, not the CMS-HCC clinical risk adjustment of beneficiaries.
- The project reports ACO-level, unweighted averages. It does not calculate CMS benchmarks, beneficiary attribution, quality scores, or financial reconciliation independently.
- Missing or inapplicable values should be interpreted using the official CMS documentation rather than automatically treated as zero.

**Data file:** `PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv` (2024 performance year; repository copy revised July 17, 2026).

Source: [CMS Shared Savings Program — Program Data](https://www.cms.gov/medicare/payment/fee-for-service-providers/shared-savings-program-ssp-acos/data).
