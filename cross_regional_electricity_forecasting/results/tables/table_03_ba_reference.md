**Table 3. Comparison with BA-reported day-ahead forecasts (hours where available).**

|   h (h) | Method                                      | nMAE % median [IQR]   |   Bias % median |   Regions |
|--------:|:--------------------------------------------|:----------------------|----------------:|----------:|
|       1 | BA day-ahead forecast (reference)           | 3.57 [2.55, 6.41]     |            0.01 |        48 |
|       1 | LightGBM, global (in-region)                | 1.14 [0.87, 1.51]     |            0.01 |        48 |
|       1 | LightGBM, global (unseen region, zero-shot) | 1.17 [0.90, 1.55]     |            0.01 |        48 |
|       1 | Seasonal naive (24 h)                       | 5.47 [4.57, 6.81]     |           -0.02 |        48 |
|       6 | BA day-ahead forecast (reference)           | 3.57 [2.55, 6.41]     |            0.01 |        48 |
|       6 | LightGBM, global (in-region)                | 3.49 [2.95, 4.35]     |            0.03 |        48 |
|       6 | LightGBM, global (unseen region, zero-shot) | 3.65 [3.03, 4.40]     |           -0.01 |        48 |
|       6 | Seasonal naive (24 h)                       | 5.47 [4.57, 6.81]     |           -0.02 |        48 |
|      24 | BA day-ahead forecast (reference)           | 3.57 [2.55, 6.41]     |            0.01 |        48 |
|      24 | LightGBM, global (in-region)                | 4.64 [3.88, 5.87]     |           -0.1  |        48 |
|      24 | LightGBM, global (unseen region, zero-shot) | 4.75 [3.91, 5.91]     |           -0.1  |        48 |
|      24 | Seasonal naive (24 h)                       | 5.47 [4.57, 6.81]     |           -0.02 |        48 |
