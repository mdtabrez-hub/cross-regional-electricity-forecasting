**Table S6. Point accuracy with spatially blocked leave-region-out folds (test period).**

|   h (h) | Method                                          | nMAE % median [IQR]   |   MASE median |
|--------:|:------------------------------------------------|:----------------------|--------------:|
|       1 | LightGBM, global (in-region)                    | 1.14 [0.87, 1.51]     |         0.194 |
|       1 | LightGBM, global (unseen region, zero-shot)     | 1.17 [0.90, 1.55]     |         0.201 |
|       1 | LightGBM, global (spatially blocked, zero-shot) | 1.27 [1.01, 1.61]     |         0.219 |
|       1 | LightGBM, local                                 | 1.28 [1.01, 1.61]     |         0.22  |
|       1 | Seasonal naive (24 h)                           | 5.48 [4.57, 6.81]     |         1.009 |
|      24 | LightGBM, global (in-region)                    | 4.64 [3.88, 5.87]     |         0.884 |
|      24 | LightGBM, global (unseen region, zero-shot)     | 4.75 [3.91, 5.91]     |         0.888 |
|      24 | LightGBM, global (spatially blocked, zero-shot) | 4.81 [4.02, 6.03]     |         0.901 |
|      24 | LightGBM, local                                 | 4.72 [3.94, 5.94]     |         0.893 |
|      24 | Seasonal naive (24 h)                           | 5.48 [4.57, 6.81]     |         1.009 |
