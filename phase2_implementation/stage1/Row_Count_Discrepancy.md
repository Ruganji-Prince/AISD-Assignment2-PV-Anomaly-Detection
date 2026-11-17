# Released-data and literature population discrepancy

Source: Lazzaretti et al. (2020), *Monitoring System for Online Fault Detection and Classification in Photovoltaic Plants*, Section 4.1, Real System Installation. DOI: https://doi.org/10.3390/s20174688. The preserved full-text XML was inspected during the approved review; the original repository is pinned by the Phase 1 source manifest.

The paper describes a 16-day experiment with acquisition around 07:30-17:00 and nominal 1 Hz sampling. Its listed counts are normal 309,253; short circuit 5,999; resistive degradation 10,371; open circuit 6,024; shade 184,311. Their sum is 515,958. This is a calculated sum of reported class counts, not necessarily a standalone total printed in the paper.

Programmatic evidence is recorded in `evidence/row_count_discrepancy.json`, using the unchanged raw CSV before cleaning. It includes `irr <= 0`, `irr < 10`, `irr < 50`, `irr < 100` and `irr >= 100`, with all five class counts for each population.

- Verified: the complete export contains 1,373,798 source positions.
- Verified: the literature class counts sum to 515,958.
- Verified by assertions: `irr >= 100 W/m^2` returns exactly 515,958 positions and every literature class count.
- Verified: the complementary `irr < 100` population contains 857,840 positions, comprising 853,678 normal and 4,162 shade labels; no hardware-fault label is removed by this diagnostic filter.
- Plausible interpretation: the paper's evaluation population may correspond to an irradiance-qualified subset.
- Not verified: the inspected source does not explicitly establish that this filter generated the reported population, identify all excluded observation times, or establish continuous timestamps.

Low irradiance is not automatically verified nighttime. No primary training/validation/test observations are removed to reproduce the literature total. The nominal acquisition frequency does not convert source positions into guaranteed consecutive seconds. The 16 signal-defined blocks remain signal-defined blocks, not verified days or sessions.
