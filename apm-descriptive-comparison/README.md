# Medicare APMs: descriptive comparison

## Question
How do MSSP, ACO REACH, and BPCI Advanced differ in participation, financial performance, quality reporting, and payment design?

## Data and approach
Secondary descriptive analysis of publicly reported CMS program and evaluation findings. No synthetic data or causal comparisons. All source tables retain a CMS URL. The programs use different populations and financial measures; do not rank them by raw savings.

- MSSP: population-based shared savings; annual ACO performance and benchmark reconciliation.
- ACO REACH: population-based risk arrangements, capitation options, and quality scoring.
- BPCI Advanced: 90-day clinical episodes; retrospective reconciliation and independent evaluation.

The included MSSP participation snapshots and final performance-year counts use different reporting bases. GPDC is the predecessor of ACO REACH. BPCI Advanced savings are evaluation estimates, unlike MSSP and ACO REACH benchmark settlements.

## Run
```bash
pip install pandas matplotlib
python apm-descriptive-comparison/analyze.py
```

Outputs: participation trends, model-specific financial plots, a REACH quality trend, and source-linked CSV tables.

## Limitations
Public summary figures do not support standardized comparisons of quality or risk-adjusted spending across models. This project does not independently reproduce beneficiary attribution, payment reconciliation, or model impacts. Reporting periods and denominators vary. The ACO REACH financial series here ends in 2023. Verify manually transcribed figures against the source URLs before publication.
