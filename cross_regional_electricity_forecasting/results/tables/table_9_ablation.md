**Table 9. Ablations of the zero-shot global model (h = 24 h, unseen BAs).**

| Variant                                     |   nMAE % median | Median rel. change vs full LRO %   | 95% CI       | Wilcoxon p (Holm)   |
|:--------------------------------------------|----------------:|:-----------------------------------|:-------------|:--------------------|
| LightGBM, global (unseen region, zero-shot) |            4.75 | reference                          |              |                     |
| LightGBM, global (in-region)                |            4.64 | -0.5                               | [-0.7, -0.4] | 6.3e-12             |
| Without calendar features                   |            5.09 | 6.7                                | [5.0, 7.0]   | 9.2e-14             |
| Without weekly lags (168, 336 h)            |            4.87 | 0.6                                | [0.5, 1.3]   | 7.8e-05             |
| Recent lags 0–3 h only (drop lags 4–23 h)   |            4.76 | 0.3                                | [0.1, 0.4]   | 7.8e-05             |
| 5 random source BAs (draw 1)                |            4.93 | 3.2                                | [2.2, 4.8]   | 9.2e-14             |
| 5 random source BAs (draw 2)                |            5    | 3.3                                | [2.6, 4.9]   | 3.2e-13             |
| 5 random source BAs (draw 3)                |            4.99 | 3.7                                | [3.1, 4.5]   | 1.6e-13             |
| 10 random source BAs (draw 1)               |            4.87 | 1.6                                | [1.1, 1.9]   | 1.2e-10             |
| 10 random source BAs (draw 2)               |            4.86 | 2.1                                | [1.4, 2.4]   | 7.4e-11             |
| 10 random source BAs (draw 3)               |            4.87 | 2.1                                | [1.6, 2.7]   | 2.1e-13             |
| 20 random source BAs (draw 1)               |            4.79 | 0.8                                | [0.4, 1.1]   | 3.6e-09             |
| 20 random source BAs (draw 2)               |            4.82 | 0.7                                | [0.3, 0.9]   | 3.5e-07             |
| 20 random source BAs (draw 3)               |            4.81 | 0.4                                | [0.2, 0.7]   | 7.8e-05             |
