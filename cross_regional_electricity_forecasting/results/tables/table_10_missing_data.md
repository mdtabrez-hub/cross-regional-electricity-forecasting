**Table 10. Median nMAE (%) of the in-region global model with corrupted inputs (test period; common scored hours).**

|   h (h) | Scenario   |   Native NaN | LOCF   | Weekly-seasonal   |   MCAR-trained, native |
|--------:|:-----------|-------------:|:-------|:------------------|-----------------------:|
|       1 | clean      |         1.14 | –      | –                 |                   1.17 |
|       1 | MCAR_10    |         1.84 | 1.68   | 2.19              |                   1.32 |
|       1 | MCAR_40    |         4.04 | 3.68   | 5.14              |                   2.29 |
|       1 | BLOCK_24h  |         1.89 | 2.52   | 1.91              |                   1.71 |
|       1 | BLOCK_168h |         1.95 | 2.42   | 1.87              |                   1.94 |
|      24 | clean      |         4.64 | –      | –                 |                   4.65 |
|      24 | MCAR_10    |         5.05 | 4.81   | 5.06              |                   4.72 |
|      24 | MCAR_40    |         6.93 | 5.98   | 6.66              |                   5.4  |
|      24 | BLOCK_24h  |         5.02 | 5.81   | 5.13              |                   4.94 |
|      24 | BLOCK_168h |         5.07 | 5.79   | 5.07              |                   5.03 |
