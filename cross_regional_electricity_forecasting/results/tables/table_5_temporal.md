**Table 5. Median nMAE (%) by evaluation year (frozen models trained on 2019–2022).**

|   h (h) | Method                                      |   2023 (validation) |   2024 |   2025 |
|--------:|:--------------------------------------------|--------------------:|-------:|-------:|
|       1 | LightGBM, global (in-region)                |                1.11 |   1.12 |   1.19 |
|       1 | LightGBM, global (unseen region, zero-shot) |                1.17 |   1.16 |   1.22 |
|       1 | LightGBM, local                             |                1.22 |   1.26 |   1.3  |
|       1 | Seasonal naive (24 h)                       |                5.34 |   5.16 |   5.56 |
|       6 | LightGBM, global (in-region)                |                3.44 |   3.49 |   3.53 |
|       6 | LightGBM, global (unseen region, zero-shot) |                3.65 |   3.64 |   3.64 |
|       6 | LightGBM, local                             |                3.57 |   3.69 |   3.8  |
|       6 | Seasonal naive (24 h)                       |                5.34 |   5.16 |   5.56 |
|      24 | LightGBM, global (in-region)                |                4.6  |   4.54 |   4.67 |
|      24 | LightGBM, global (unseen region, zero-shot) |                4.67 |   4.56 |   4.72 |
|      24 | LightGBM, local                             |                4.56 |   4.49 |   4.8  |
|      24 | Seasonal naive (24 h)                       |                5.34 |   5.16 |   5.56 |
