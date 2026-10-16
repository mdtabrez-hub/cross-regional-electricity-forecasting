"""Generate manuscript tables (CSV + Markdown) from saved metrics.

Usage: python -m src.generate_tables
Outputs: results/tables/table_*.csv|.md, results/tables/table_manifest.csv
"""
from __future__ import annotations

import pandas as pd

from .common import DATA_PROCESSED, LOG_DIR, METRIC_DIR, ROOT, TABLE_DIR

MANIFEST = []

LABEL = {"SN24": "Seasonal naive (24 h)", "SN168": "Seasonal naive (168 h)", "PERS": "Persistence",
         "RIDGE_G_IN": "Ridge, global (in-region)", "RIDGE_G_LRO": "Ridge, global (unseen region)",
         "LGB_L": "LightGBM, local", "LGB_G_IN": "LightGBM, global (in-region)",
         "LGB_G_LRO": "LightGBM, global (unseen region, zero-shot)", "BA_DA": "BA day-ahead forecast (reference)"}


def save(df: pd.DataFrame, name: str, caption: str, source: str):
    df.to_csv(TABLE_DIR / f"{name}.csv", index=False)
    (TABLE_DIR / f"{name}.md").write_text(f"**{caption}**\n\n" + df.to_markdown(index=False) + "\n")
    MANIFEST.append({"table": name, "caption": caption, "source_files": source, "script": "src/generate_tables.py"})


def fmt_iqr(df, m, scale=100, nd=2):
    return df.apply(lambda r: f"{r[f'{m}_median']*scale:.{nd}f} [{r[f'{m}_q25']*scale:.{nd}f}, {r[f'{m}_q75']*scale:.{nd}f}]", axis=1)


def t_regions():
    r = pd.read_csv(DATA_PROCESSED / "regions.csv", index_col=0).sort_values("mean_demand_mw", ascending=False)
    folds = pd.read_json(LOG_DIR / "selected_hyperparameters.json", typ="series")["lro_folds"]
    t = pd.DataFrame({"BA": r.index, "Name": r.label.str.replace("_", " ").str.replace("tuscon", "tucson").str.replace("pugent", "puget")
                      .str.title().str.replace(" Iso", " ISO").str.replace(" And ", " and ").str.replace(" Of ", " of "), "Interconnect": r.interconnect_code_eia,
                      "Mean demand (MW)": r.mean_demand_mw.round(0).astype(int),
                      "Reported coverage (%)": (100 * r.reported_coverage).round(2),
                      "PUDL-flagged (%)": (100 * r.flagged_share).round(2),
                      "LRO fold": [folds[b] for b in r.index]})
    save(t, "table_A1_regions", "Table A1. Balancing authorities included in the study (2019–2025).",
         "data/processed/regions.csv")


def t_point():
    s = pd.read_csv(METRIC_DIR / "point_metrics_summary.csv")
    order = ["SN24", "SN168", "PERS", "RIDGE_G_IN", "RIDGE_G_LRO", "LGB_L", "LGB_G_IN", "LGB_G_LRO"]
    s["order"] = s.method.map({m: i for i, m in enumerate(order)})
    s = s[~((s.method == "PERS") & (s.h == 24))]  # identical to SN24 at h = 24 by construction
    s = s.sort_values(["h", "order"])
    t = pd.DataFrame({"h (h)": s.h, "Method": s.method.map(LABEL), "nMAE % median [IQR]": fmt_iqr(s, "nMAE"),
                      "nRMSE % median": (100 * s.nRMSE_median).round(2), "MASE median": s.MASE_median.round(3),
                      "Bias % median": (100 * s.bias_pct_median).map(lambda v: f"{v:.2f}".replace("-0.00", "0.00")),
                      "Regions": s.n_regions})
    save(t, "table_2_point_accuracy", "Table 2. Test-period (2024–2025) point accuracy across 48 BAs.",
         "results/metrics/point_metrics_summary.csv")


def t_tests():
    t = pd.read_csv(METRIC_DIR / "paired_tests_point.csv")
    t = t[t.metric == "nMAE"]
    out = pd.DataFrame({"h (h)": t.h, "A": t.method_a.map(LABEL), "B": t.method_b.map(LABEL),
                        "Median rel. change in nMAE (A vs B) %": (100 * t.median_rel_change).round(1),
                        "95% CI (regions bootstrap)": t.apply(lambda r: f"[{100*r.rel_ci_lo:.1f}, {100*r.rel_ci_hi:.1f}]", axis=1),
                        "A better (share of BAs)": t.share_a_better.round(2),
                        "Wilcoxon p (Holm, all)": t.p_holm_all.map(lambda p: f"{p:.2g}")})
    blk = pd.read_csv(METRIC_DIR / "block_bootstrap_summary.csv")
    out = out.merge(pd.DataFrame({"h (h)": blk.h, "A": blk.method_a.map(LABEL), "B": blk.method_b.map(LABEL),
                                  "BAs with A sig. better (block bootstrap)": blk.share_a_better_sig.round(2),
                                  "BAs with B sig. better": blk.share_b_better_sig.round(2)}),
                    on=["h (h)", "A", "B"], how="left").fillna("–")
    save(out, "table_S4_paired_tests_full", "Table S4. All paired comparisons of per-BA nMAE (test period).",
         "results/metrics/paired_tests_point.csv; results/metrics/block_bootstrap_summary.csv")


def t_adapt():
    s = pd.read_csv(METRIC_DIR / "adaptation_metrics_summary.csv")
    lab = dict(LABEL)
    for k in (1, 4, 13):
        lab[f"LGB_L_k{k}"] = f"LightGBM local, {k} wk target data"
        lab[f"LGB_FT_k{k}"] = f"Global fine-tuned, {k} wk target data"
    order = ["SN24", "LGB_G_LRO", "LGB_L_k1", "LGB_FT_k1", "LGB_L_k4", "LGB_FT_k4", "LGB_L_k13", "LGB_FT_k13", "LGB_L", "LGB_G_IN"]
    s = s[s.method.isin(order)].copy()
    s["o"] = s.method.map({m: i for i, m in enumerate(order)})
    s = s.sort_values(["h", "o"])
    t = pd.DataFrame({"h (h)": s.h, "Method": s.method.map(lab), "nMAE % median [IQR]": fmt_iqr(s, "nMAE"),
                      "MASE median": s.MASE_median.round(3)})
    save(t, "table_4_adaptation", "Table 4. Limited target-data adaptation for unseen BAs (test 2024–2025).",
         "results/metrics/adaptation_metrics_summary.csv")


def t_temporal():
    s = pd.read_csv(METRIC_DIR / "temporal_metrics_summary.csv")
    s = s[s.by == "year"]
    t = s.pivot_table(index=["h", "method"], columns="period", values="nMAE_median").reset_index()
    t["method"] = t.method.map(LABEL)
    for c in t.columns[2:]:
        t[c] = (100 * t[c]).round(2)
    r = pd.read_csv(METRIC_DIR / "refit_metrics_summary.csv")
    rr = r.pivot_table(index="h", columns="method", values="nMAE_median").reset_index()
    t2 = pd.DataFrame({"h (h)": rr.h,
                       "Global frozen (2025) %": (100 * rr.LGB_G_IN).round(2),
                       "Global refit (2025) %": (100 * rr.LGB_G_IN_refit).round(2),
                       "Local frozen (2025) %": (100 * rr.LGB_L).round(2),
                       "Local refit (2025) %": (100 * rr.LGB_L_refit).round(2)})
    save(t.rename(columns={"h": "h (h)", "method": "Method"}), "table_5_temporal",
         "Table 5. Median nMAE (%) by evaluation year (frozen models trained on 2019–2022).",
         "results/metrics/temporal_metrics_summary.csv")
    save(t2, "table_6_refit", "Table 6. Frozen vs. refit (rolling origin) models on 2025: median nMAE (%).",
         "results/metrics/refit_metrics_summary.csv")


def t_prob():
    s = pd.read_csv(METRIC_DIR / "probabilistic_summary.csv")
    s = s[s.period == "all"]
    order = ["QR", "SCP", "CQR", "SCP-T4", "ACI-CQR", "ACI-CQR-V"]
    s["o"] = s.method.map({m: i for i, m in enumerate(order)})
    s = s.sort_values(["alpha", "h", "setting", "o"])
    t = pd.DataFrame({"Nominal": (100 * (1 - s.alpha)).round(0).astype(int).astype(str) + "%", "h (h)": s.h,
                      "Setting": s.setting, "Method": s.method,
                      "Mean coverage %": (100 * s.coverage_mean).round(1),
                      "Min–max coverage %": s.apply(lambda r: f"{100*r.coverage_min:.1f}–{100*r.coverage_max:.1f}", axis=1),
                      "Mean |cov. dev.| pp": (100 * s.mean_abs_cov_dev).round(1),
                      "BAs under-covered >5 pp": (100 * s.share_regions_undercover_5pp).round(0),
                      "Median hourly width %": (100 * s.width_hour_median_norm_median).round(2),
                      "Mean width %": (100 * s.width_norm_median).round(2),
                      "Median interval score %": (100 * s.interval_score_norm_median).round(2)})
    save(t, "table_S1_probabilistic_full", "Table S1. Interval calibration on the test period, all settings (48 BAs).",
         "results/metrics/probabilistic_summary.csv")


def t_aci_sens():
    s = pd.read_csv(METRIC_DIR / "aci_gamma_sensitivity_summary.csv")
    t = pd.DataFrame({"h (h)": s.h, "γ": s.gamma, "Mean coverage %": (100 * s.coverage_mean).round(1),
                      "Min coverage %": (100 * s.coverage_min).round(1),
                      "Median hourly width % of mean load": (100 * s.width_hour_median_norm_median).round(2),
                      "Median interval score %": (100 * s.interval_score_norm_median).round(2),
                      "Capped hours %": (100 * s.capped_share_mean).round(2)})
    save(t, "table_S2_aci_sensitivity", "Table S2. POST-HOC test-set sensitivity of ACI-CQR (90%, unseen BAs) to the "
         "step size γ (not used for any selection).", "results/metrics/aci_gamma_sensitivity_summary.csv")


def t_missing():
    s = pd.read_csv(METRIC_DIR / "missing_data_summary.csv")
    t = pd.DataFrame({"h (h)": s.h, "Scenario": s.scenario, "Strategy": s.strategy, "Model": s.method,
                      "Input missing %": (100 * s.input_missing_share).round(1),
                      "nMAE % median": (100 * s.nMAE_median).round(2), "nMAE % mean": (100 * s.nMAE_mean).round(2),
                      "Min. scored share of hours": s.min_coverage_of_eval_hours.round(3)})
    save(t, "table_S3_missing_data_full", "Table S3. Robustness to missing input observations, all scenarios (test period; common scored hours).",
         "results/metrics/missing_data_summary.csv")


ABL = {"no_calendar": "Without calendar features", "no_weekly_lags": "Without weekly lags (168, 336 h)",
       "recent_lags_0_3_only": "Recent lags 0–3 h only (drop lags 4–23 h)"}


def abl_label(m):
    if m.startswith("pool_"):
        _, n, rep = m.split("_")
        return f"{n} random source BAs (draw {int(rep[3:]) + 1})"
    return ABL.get(m, LABEL.get(m, m))


def t_ablation():
    s = pd.read_csv(METRIC_DIR / "ablation_results.csv")
    s["o"] = s.method.map(lambda m: (0 if m == "LGB_G_LRO" else 1 if m == "LGB_G_IN" else 2 if m in ABL else
                                     3 + int(m.split("_")[1]) if m.startswith("pool_") else 9))
    s = s.sort_values(["o", "method"])
    t = pd.DataFrame({"Variant": s.method.map(abl_label), "nMAE % median": (100 * s.nMAE_median).round(2),
                      "Median rel. change vs full LRO %": (100 * s.median_rel_change).map(lambda v: "reference" if pd.isna(v) else f"{v:.1f}"),
                      "95% CI": s.apply(lambda r: "" if pd.isna(r.rel_ci_lo) else f"[{100*r.rel_ci_lo:.1f}, {100*r.rel_ci_hi:.1f}]", axis=1),
                      "Wilcoxon p (Holm)": s.p_holm.map(lambda p: "" if pd.isna(p) else f"{p:.2g}")})
    save(t, "table_10_ablation", "Table 10. Ablations of the zero-shot global model (h = 24 h, unseen BAs).",
         "results/metrics/ablation_results.csv")


def t_compute():
    c = pd.read_csv(LOG_DIR / "compute_costs_point.csv")
    c["family"] = c.model.str.replace(r"_q\d\d$", " (quantile)", regex=True)
    g = c.groupby(["family", "h"]).agg(fits=("model", "size"), fit_s_mean=("fit_seconds", "mean"),
                                       inference_s_mean=("inference_seconds", "mean"),
                                       n_inf=("n_inference_rows", "mean"), size_mb=("size_bytes", "mean"),
                                       trees=("n_trees", "mean"), peak_rss=("peak_rss_mb", "max")).reset_index()
    t = pd.DataFrame({"Model": g.family, "h (h)": g.h, "Fits": g.fits, "Mean fit time (s)": g.fit_s_mean.round(1),
                      "Inference (µs/forecast)": (1e6 * g.inference_s_mean / g.n_inf).round(2),
                      "Model size (MB)": (g.size_mb / 1e6).round(2), "Trees": g.trees.round(0),
                      "Peak RSS of run (MB)": g.peak_rss.round(0)})
    a = LOG_DIR / "compute_costs_adapt.csv"
    save(t, "table_11_compute", "Table 11. Computational cost (4-core CPU).", "results/logs/compute_costs_point.csv")
    if a.exists():
        aa = pd.read_csv(a)
        save(aa.round(3), "table_S10_compute_adaptation", "Table 10b. Adaptation fit time per target BA (s).",
             "results/logs/compute_costs_adapt.csv")


def t_ba():
    s = pd.read_csv(METRIC_DIR / "ba_dayahead_summary.csv")
    t = pd.DataFrame({"h (h)": s.h, "Method": s.method.map(LABEL), "nMAE % median [IQR]": fmt_iqr(s, "nMAE"),
                      "Bias % median": (100 * s.bias_pct_median).round(2), "Regions": s.n_regions})
    save(t, "table_12_ba_reference", "Table 12. Comparison with BA-reported day-ahead forecasts (hours where available).",
         "results/metrics/ba_dayahead_summary.csv")


def t_tests_main():
    t = pd.read_csv(METRIC_DIR / "paired_tests_point.csv")
    t = t[(t.metric == "nMAE")]
    keep = [("LGB_G_LRO", "LGB_G_IN"), ("LGB_G_IN", "LGB_L"), ("LGB_G_LRO", "LGB_L"), ("LGB_G_LRO", "SN24")]
    t = t[[(a, b) in keep for a, b in zip(t.method_a, t.method_b)]]
    blk = pd.read_csv(METRIC_DIR / "block_bootstrap_summary.csv")
    t = t.merge(blk[["h", "method_a", "method_b", "share_a_better_sig", "share_b_better_sig"]], on=["h", "method_a", "method_b"], how="left")
    short = {"LGB_G_LRO": "G-LRO (zero-shot)", "LGB_G_IN": "G-IN", "LGB_L": "Local", "SN24": "SN24"}
    out = pd.DataFrame({"h (h)": t.h, "A vs B": t.method_a.map(short) + " vs " + t.method_b.map(short),
                        "Median rel. change %": (100 * t.median_rel_change).round(1),
                        "95% CI": t.apply(lambda r: f"[{100*r.rel_ci_lo:.1f}, {100*r.rel_ci_hi:.1f}]", axis=1),
                        "A better (BAs %)": (100 * t.share_a_better).round(0),
                        "A sig. better / B sig. better (block bootstrap, BAs %)": t.apply(
                            lambda r: f"{100*r.share_a_better_sig:.0f} / {100*r.share_b_better_sig:.0f}", axis=1),
                        "Holm p": t.p_holm_all.map(lambda p: f"{p:.1g}" if p >= 1e-4 else "<1e-4")})
    save(out.sort_values(["h (h)"]), "table_3_paired_tests",
         "Table 3. Key paired comparisons of per-BA nMAE (test period; negative = A more accurate).",
         "results/metrics/paired_tests_point.csv; results/metrics/block_bootstrap_summary.csv")


def t_prob_main():
    s = pd.read_csv(METRIC_DIR / "probabilistic_summary.csv")
    s = s[(s.period == "all") & (s.alpha == 0.1) & (s.setting == "unseen-region")]
    order = ["QR", "SCP", "CQR", "SCP-T4", "ACI-CQR", "ACI-CQR-V"]
    s = s[s.method.isin(order)].assign(o=lambda d: d.method.map({m: i for i, m in enumerate(order)})).sort_values(["h", "o"])
    lab = {"ACI-CQR": "ACI-CQR (γ = 0.005, frozen protocol)", "ACI-CQR-V": "ACI-CQR-V (γ on held-out BAs' 2023 data; exploratory)"}
    t = pd.DataFrame({"h (h)": s.h, "Method": s.method.map(lambda m: lab.get(m, m)),
                      "Mean cov. %": (100 * s.coverage_mean).round(1),
                      "Min–max cov. %": s.apply(lambda r: f"{100*r.coverage_min:.1f}–{100*r.coverage_max:.1f}", axis=1),
                      "BAs > 5 pp under %": (100 * s.share_regions_undercover_5pp).round(0),
                      "Median hourly width %": (100 * s.width_hour_median_norm_median).round(2),
                      "Median IS %": (100 * s.interval_score_norm_median).round(2)})
    save(t, "table_7_probabilistic", "Table 7. Calibration of nominal 90% intervals for unseen BAs (random folds, test "
         "period). Widths and interval scores (IS) are in % of mean load.", "results/metrics/probabilistic_summary.csv")


def t_rev_calibration():
    f = METRIC_DIR / "rev_calibration_summary.csv"
    if not f.exists():
        return
    s = pd.read_csv(f)
    t = pd.DataFrame({"Setting": s.setting, "h (h)": s.h, "Method": s.method,
                      "Mean cov. %": (100 * s.coverage_mean).round(1),
                      "Min–max cov. %": s.apply(lambda r: f"{100*r.coverage_min:.1f}–{100*r.coverage_max:.1f}", axis=1),
                      "BAs > 5 pp under %": (100 * s.share_under_5pp).round(0),
                      "Median hourly width %": (100 * s.width_p50_median).round(2),
                      "Median IS %": (100 * s.IS_median).round(2)})
    save(t, "table_8_calibration_revision", "Table 8. Online and source-only calibration of 90% intervals for unseen BAs, "
         "including spatially blocked folds (post-review analyses; γ selected on source BAs only for ACI-CQR-S).",
         "results/metrics/rev_calibration_summary.csv")


def t_missing_main():
    s = pd.read_csv(METRIC_DIR / "missing_data_summary.csv")
    s = s[s.method.isin(["LGB_G_IN", "LGB_G_IN_AUG"]) & s.scenario.isin(["clean", "MCAR_10", "MCAR_40", "BLOCK_24h", "BLOCK_168h"])]
    s["col"] = s.apply(lambda r: "MCAR-trained, native" if r.method == "LGB_G_IN_AUG" else
                       {"native": "Native NaN", "locf": "LOCF", "seasonal": "Weekly-seasonal"}[r.strategy], axis=1)
    piv = s.pivot_table(index=["h", "scenario"], columns="col", values="nMAE_median").mul(100).round(2).reset_index()
    order = {"clean": 0, "MCAR_10": 1, "MCAR_40": 2, "BLOCK_24h": 3, "BLOCK_168h": 4}
    piv = piv.sort_values(["h", "scenario"], key=lambda c: c.map(order) if c.name == "scenario" else c)
    piv = piv.rename(columns={"h": "h (h)", "scenario": "Scenario"})
    cols = ["h (h)", "Scenario", "Native NaN", "LOCF", "Weekly-seasonal", "MCAR-trained, native"]
    save(piv[[c for c in cols if c in piv]].fillna("–"), "table_9_missing_data",
         "Table 9. Median nMAE (%) of the in-region global model with corrupted inputs (test period; common scored hours).",
         "results/metrics/missing_data_summary.csv")


def t_supplementary_revision():
    f = METRIC_DIR / "rev_adapt_origins_summary.csv"
    if f.exists():
        s = pd.read_csv(f)
        piv = s.pivot_table(index=["h", "origin"], columns="method", values="nMAE_median").mul(100).round(2).reset_index()
        save(piv, "table_S5_adaptation_origins", "Table S5. Median nMAE (%) for unseen BAs at three additional onboarding "
             "origins (evaluation: the following 365 days).", "results/metrics/rev_adapt_origins_summary.csv")
    f = METRIC_DIR / "rev_spatial_summary.csv"
    if f.exists():
        s = pd.read_csv(f)
        t = pd.DataFrame({"h (h)": s.h, "Method": s.method.map(lambda m: LABEL.get(m, "LightGBM, global (spatially blocked, zero-shot)" if m == "LGB_G_LRS" else m)),
                          "nMAE % median [IQR]": fmt_iqr(s, "nMAE"), "MASE median": s.MASE_median.round(3)})
        save(t, "table_S6_spatial", "Table S6. Point accuracy with spatially blocked leave-region-out folds (test period).",
             "results/metrics/rev_spatial_summary.csv")
    f = METRIC_DIR / "rev_excluded_bas.csv"
    if f.exists():
        s = pd.read_csv(f)
        t = pd.DataFrame({"h (h)": s.h, "BA": s.region, "Mean MW": s.mean_mw.round(0), "Zero-shot nMAE %": (100 * s.nMAE_zero_shot).round(2),
                          "Local nMAE %": (100 * s.nMAE_local).round(2), "SN24 nMAE %": (100 * s.nMAE_SN24).round(2)})
        save(t, "table_S7_excluded_bas", "Table S7. Zero-shot forecasts for the five BAs excluded by the selection criteria.",
             "results/metrics/rev_excluded_bas.csv")
    f = METRIC_DIR / "rev_conditional_coverage.csv"
    if f.exists():
        s = pd.read_csv(f)
        s = s[s.method.str.startswith(("CQR", "ACI-CQR-S"))]
        t = pd.DataFrame({"Setting": s.setting, "h (h)": s.h, "Method": s.method, "Conditioning": s.by, "Level": s.level,
                          "Mean cov. over BAs %": (100 * s.coverage_mean_over_BAs).round(1),
                          "Min cov. over BAs %": (100 * s.coverage_min_over_BAs).round(1)})
        save(t, "table_S8_conditional_coverage", "Table S8. Conditional coverage of 90% intervals by season and by "
             "within-BA load decile (0 = lowest).", "results/metrics/rev_conditional_coverage.csv")
    f = LOG_DIR / "ridge_alpha_grid_validation.csv"
    if f.exists():
        s = pd.read_csv(f)
        save(s.assign(val_es_median_nmae=(100 * s.val_es_median_nmae).round(3)).rename(
            columns={"alpha": "Ridge penalty λ", "val_es_median_nmae": "Validation median nMAE %"}),
             "table_S9_ridge_grid", "Table S9. Ridge penalty grid on the validation (odd ISO) weeks, h = 24 h.",
             "results/logs/ridge_alpha_grid_validation.csv")


def main():
    for fn in (t_regions, t_point, t_tests, t_tests_main, t_adapt, t_temporal, t_prob, t_prob_main, t_rev_calibration,
               t_aci_sens, t_missing, t_missing_main, t_ablation, t_compute, t_ba, t_supplementary_revision):
        try:
            fn()
        except FileNotFoundError as e:
            print(f"skip {fn.__name__}: {e}")
    pd.DataFrame(MANIFEST).to_csv(ROOT / "results" / "tables" / "table_manifest.csv", index=False)


if __name__ == "__main__":
    main()
