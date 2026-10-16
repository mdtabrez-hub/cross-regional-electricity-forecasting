# Introduction

Short-term electricity-demand forecasts underpin unit commitment, reserve procurement, interchange scheduling and market operations. Every balancing authority (BA) in the United States produces them, and their errors translate directly into reserve and balancing costs [@hong2016probabilistic]. Most published forecasting studies, however, train and test on the same system. In practice, three situations call for a model that works on a system it has not seen:

- a new or reorganised balancing area;
- a utility joining a market;
- a small BA without a dedicated forecasting team.

A forecaster that generalises across regions, and whose prediction intervals remain trustworthy when it does, has engineering value beyond a marginal accuracy gain on a familiar system.

Two developments make cross-region forecasting plausible. First, *global* models fitted jointly to many series often match or outperform per-series models [@montero2021principles; @makridakis2022m5]. Second, pre-trained time-series foundation models promise zero-shot forecasting [@ansari2024chronos; @das2024decoder]. Whether such transfer works for system-level electricity demand, and at what cost to uncertainty quantification, is a question of distribution shift. An unseen BA differs from the training BAs in size, climate, customer mix and data-collection practice (geographic shift), and every BA changes over time through load growth, electrification, behind-the-meter solar and membership changes (temporal shift).

Conformal prediction offers distribution-free coverage guarantees, but only under exchangeability [@vovk2005algorithmic]. Adaptive variants recover long-run coverage under drift [@gibbs2021adaptive; @zaffran2022adaptive]. Their behaviour under geographic shift, under the delayed feedback inherent in day-ahead forecasting, and in the start-up period on a new system has not been characterised for system-level load.

This paper asks five research questions:

- **RQ1.** How much does forecast accuracy deteriorate when a BA is excluded from training, compared with in-region global and local models?
- **RQ2.** How much do one to thirteen weeks of target-region data help, through local training or fine-tuning of a global model?
- **RQ3.** Do quantile-regression and conformal prediction intervals remain calibrated under geographic and temporal shift?
- **RQ4.** How robust are the forecasts to temporal drift and to missing input observations?
- **RQ5.** What are the trade-offs among accuracy, interval reliability, computational cost and adaptation data?

The paper is organised as follows. Section 2 reviews related work and Section 3 states the research gap and contributions. Section 4 describes the data, Section 5 formulates the problem, Section 6 presents the methods, Section 7 details the experimental design and Section 8 the metrics. Section 9 reports the results and Section 10 discusses them. Section 11 covers robustness and ablations and Section 12 computational cost. Practical implications, limitations and threats to validity follow in Sections 13–15, and Section 16 concludes.
