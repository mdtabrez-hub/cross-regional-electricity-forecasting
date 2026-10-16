"""Publication figures from saved data and metrics (PNG 600 dpi + vector PDF).

Font: Times New Roman is requested first; if it is not installed, the metric-compatible
Liberation Serif is used (the case in the environment that produced the submitted
figures; recorded in figures/figure_manifest.csv).

Usage: python -m src.generate_figures
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from .common import DATA_META, DATA_PROCESSED, FIG_DIR, LOG_DIR, METRIC_DIR, PRED_DIR, load_config  # noqa: E402
from .conformal import aci_intervals, conformal_quantile, cqr_scores  # noqa: E402

AVAILABLE = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Times New Roman" if "Times New Roman" in AVAILABLE else "Liberation Serif"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 8.5, "axes.spines.top": False,
    "axes.spines.right": False, "savefig.bbox": "tight", "savefig.pad_inches": 0.03, "pdf.fonttype": 42,
})
# Colour-blind-safe palette (Okabe–Ito)
C = {"SN24": "#999999", "SN168": "#BBBBBB", "PERS": "#666666", "RIDGE_G_IN": "#CC79A7", "RIDGE_G_LRO": "#E3A8C9",
     "LGB_L": "#E69F00", "LGB_G_IN": "#0072B2", "LGB_G_LRO": "#56B4E9", "BA_DA": "#009E73", "FT": "#D55E00",
     "LOC": "#E69F00"}
LAB = {"SN24": "Seasonal naive 24 h", "SN168": "Seasonal naive 168 h", "PERS": "Persistence",
       "RIDGE_G_IN": "Ridge global (in)", "RIDGE_G_LRO": "Ridge global (unseen)", "LGB_L": "LightGBM local",
       "LGB_G_IN": "LightGBM global (in)", "LGB_G_LRO": "LightGBM global (unseen)", "BA_DA": "BA day-ahead"}
W1, W2 = 3.5, 7.16  # single / double column width (in)
MANIFEST = []


def save(fig, name, caption, sources):
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"{name}.{ext}", dpi=600)
    plt.close(fig)
    MANIFEST.append({"figure": name, "caption": caption, "source_data": sources, "script": "src/generate_figures.py",
                     "font": FONT, "formats": "png (600 dpi); pdf (vector)"})


def panel_label(ax, s):
    ax.text(-0.12, 1.04, s, transform=ax.transAxes, fontweight="bold", fontsize=11, va="bottom")


# ----------------------------------------------------------------------------- 1 workflow
def fig_workflow():
    fig, ax = plt.subplots(figsize=(W2, 3.4))
    ax.axis("off")
    texts = ["1  Data\nEIA-930 via PUDL v2026.10.0\n72 BAs, hourly",
             "2  Screening and selection\n48 BAs, 2019–2025\ncausal input cleaning",
             "3  Features (past only)\ninstance scaling\nh = 1, 6, 24 h",
             "4  Models\nnaive, ridge, LightGBM\nlocal / global / leave-out",
             "5  Adaptation, intervals\nfine-tuning on k weeks\nQR, SCP, CQR, ACI",
             "6  Test 2024–2025\naccuracy, calibration,\ndrift, missing data, cost"]
    bw, bh = 2.6, 1.0
    pos = [(0, 1.55), (3.4, 1.55), (6.8, 1.55), (6.8, 0.15), (3.4, 0.15), (0, 0.15)]
    for (x, y), t in zip(pos, texts):
        ax.add_patch(FancyBboxPatch((x, y), bw, bh, boxstyle="round,pad=0.05", fc="#EAF2FA", ec="#0072B2", lw=0.9))
        ax.text(x + bw / 2, y + bh / 2, t, ha="center", va="center", fontsize=8, linespacing=1.25)
    arrow = dict(arrowstyle="->", lw=1.0)
    for i in range(5):
        (x0, y0), (x1, y1) = pos[i], pos[i + 1]
        if y0 == y1:
            if x1 > x0:
                ax.annotate("", xy=(x1 - 0.08, y1 + bh / 2), xytext=(x0 + bw + 0.08, y0 + bh / 2), arrowprops=arrow)
            else:
                ax.annotate("", xy=(x1 + bw + 0.08, y1 + bh / 2), xytext=(x0 - 0.08, y0 + bh / 2), arrowprops=arrow)
        else:
            ax.annotate("", xy=(x1 + bw / 2, y1 + bh + 0.08), xytext=(x0 + bw / 2, y0 - 0.08), arrowprops=arrow)
    ax.text(4.7, -0.45, "Splits: train 2019–2022 | validation 2023 (odd ISO weeks: early stopping; even weeks: "
            "conformal calibration) | test 2024–2025\nLeave-regions-out: 6 folds of 8 BAs, each excluded from "
            "fitting, early stopping and calibration", ha="center", va="center", fontsize=7.5)
    ax.set_xlim(-0.15, 9.55)
    ax.set_ylim(-0.75, 2.65)
    save(fig, "fig01_workflow", "Research workflow and leakage-resistant evaluation design.", "design (no data)")


# ----------------------------------------------------------------------------- 2 coverage
def fig_coverage():
    reg = pd.read_csv(DATA_PROCESSED / "regions.csv", index_col=0).sort_values("mean_demand_mw")
    q = pd.read_csv(DATA_META / "quality_by_region_year.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(W2, 6.2), gridspec_kw={"width_ratios": [1, 1.25]})
    col = reg.interconnect_code_eia.map({"eastern": "#0072B2", "western": "#D55E00", "ercot": "#009E73"})
    a.barh(range(len(reg)), reg.mean_demand_mw, color=col)
    a.set_xscale("log")
    a.set_yticks(range(len(reg)), reg.index, fontsize=7)
    a.set_xlabel("Mean demand 2019–2025 (MW, log scale)")
    from matplotlib.patches import Patch
    a.legend(handles=[Patch(color=c, label=k) for k, c in
                      {"Eastern": "#0072B2", "Western": "#D55E00", "ERCOT": "#009E73"}.items()],
             loc="lower right", frameon=False, title="Interconnection", title_fontsize=8.5)
    a.set_ylim(-0.6, len(reg) - 0.4)
    panel_label(a, "(a)")
    piv = q.pivot(index="region", columns="year", values="flagged").reindex(reg.index) * 100
    im = b.imshow(piv.to_numpy(), aspect="auto", cmap="Oranges", vmin=0, vmax=max(2, np.nanpercentile(piv, 99)),
                  origin="lower")
    b.set_yticks(range(len(reg)), reg.index, fontsize=7)
    b.set_xticks(range(piv.shape[1]), piv.columns)
    b.set_xlabel("Year")
    cb = fig.colorbar(im, ax=b, fraction=0.05, pad=0.02)
    cb.set_label("Hours flagged or missing (%)")
    panel_label(b, "(b)")
    fig.tight_layout()
    save(fig, "fig02_dataset_coverage", "Selected balancing authorities: (a) mean demand by interconnection; "
         "(b) share of hours flagged by PUDL screening or missing, by year.",
         "data/processed/regions.csv; data/metadata/quality_by_region_year.csv")


# ----------------------------------------------------------------------------- 3 series
def fig_series():
    panel = pd.read_parquet(DATA_PROCESSED / "panel.parquet")
    pick = ["ERCO", "CISO", "SCL"]
    fig, axes = plt.subplots(2, 1, figsize=(W2, 4.2))
    for ax, (s, e, title) in zip(axes, [("2023-01-09", "2023-01-23", "Winter (9–22 January 2023)"),
                                        ("2023-07-10", "2023-07-24", "Summer (10–23 July 2023)")]):
        for r, c in zip(pick, ["#0072B2", "#D55E00", "#009E73"]):
            d = panel[(panel.region == r) & (panel.time_utc >= s) & (panel.time_utc < e)]
            mean = panel[panel.region == r].target.mean()
            ax.plot(d.time_utc, d.target / mean, lw=0.9, color=c, label=f"{r} (mean {mean/1000:,.1f} GW)")
        ax.set_ylabel("Demand / BA mean")
        ax.set_title(title, loc="left")
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d %b"))
    axes[0].legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.32))
    axes[1].set_xlabel("UTC date")
    fig.tight_layout()
    save(fig, "fig03_example_series", "Normalised hourly demand of three BAs of different size and climate "
         "(validation year 2023; test data not shown).", "data/processed/panel.parquet")


# ----------------------------------------------------------------------------- 4 quality
def fig_quality():
    codes = pd.read_csv(DATA_META / "imputation_codes_by_region.csv", index_col=0)
    reg = pd.read_csv(DATA_PROCESSED / "regions.csv", index_col=0).sort_values("mean_demand_mw", ascending=False)
    codes = codes.reindex(reg.index).fillna(0)
    total = codes.sum(axis=1)
    flagged = codes.drop(columns=[c for c in codes.columns if c == "none"])
    keep = flagged.sum().sort_values(ascending=False).index
    share = flagged[keep].div(total, axis=0) * 100
    fig, ax = plt.subplots(figsize=(W2, 3.0))
    bottom = np.zeros(len(share))
    pal = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#56B4E9", "#F0E442", "#000000", "#999999"]
    for i, c in enumerate(keep):
        ax.bar(range(len(share)), share[c], bottom=bottom, color=pal[i % len(pal)], label=c.replace("_", " "), width=0.8)
        bottom += share[c].to_numpy()
    ax.set_xticks(range(len(share)), share.index, rotation=90, fontsize=7)
    ax.set_ylabel("Hours flagged (%)")
    ax.legend(ncol=4, frameon=False, fontsize=7.5, loc="upper right")
    ax.set_xlim(-0.6, len(share) - 0.4)
    fig.tight_layout()
    save(fig, "fig04_data_quality", "PUDL screening codes by BA (2019–2025, sorted by mean demand). Flagged hours are "
         "excluded from scoring; model inputs use an independent causal screen.",
         "data/metadata/imputation_codes_by_region.csv")


# ----------------------------------------------------------------------------- 5 accuracy
def fig_accuracy():
    pr = pd.read_csv(METRIC_DIR / "point_metrics_by_region.csv")
    order = ["SN24", "SN168", "RIDGE_G_IN", "RIDGE_G_LRO", "LGB_L", "LGB_G_IN", "LGB_G_LRO"]
    hs = sorted(pr.h.unique())
    fig, axes = plt.subplots(1, len(hs), figsize=(W2, 3.0), sharey=False)
    for ax, h in zip(axes, hs):
        data = [pr[(pr.h == h) & (pr.method == m)].nMAE.to_numpy() * 100 for m in order]
        bp = ax.boxplot(data, patch_artist=True, widths=0.65, showfliers=True,
                        flierprops=dict(markersize=2, alpha=0.5), medianprops=dict(color="k", lw=1))
        for p, m in zip(bp["boxes"], order):
            p.set_facecolor(C[m])
            p.set_linewidth(0.6)
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.5, 1, 2, 3, 5, 10, 20]))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_title(f"h = {h} h", loc="left")
        ax.set_xticks(range(1, len(order) + 1), [LAB[m] for m in order], rotation=60, ha="right", fontsize=7.5)
    axes[0].set_ylabel("nMAE per BA (%, log scale)")
    fig.tight_layout()
    save(fig, "fig05_accuracy", "Distribution of per-BA test nMAE (2024–2025) by method and horizon.",
         "results/metrics/point_metrics_by_region.csv")


# ----------------------------------------------------------------------------- 6 regions
def fig_regions():
    pr = pd.read_csv(METRIC_DIR / "point_metrics_by_region.csv")
    reg = pd.read_csv(DATA_PROCESSED / "regions.csv", index_col=0)
    fig, axes = plt.subplots(1, 2, figsize=(W2, 3.1))
    h = 24
    piv = pr[pr.h == h].pivot(index="region", columns="method", values="nMAE") * 100
    ax = axes[0]
    mx = np.nanmax(piv[["LGB_G_IN", "LGB_G_LRO"]].to_numpy()) * 1.1
    sc = ax.scatter(piv.LGB_G_IN, piv.LGB_G_LRO, s=14, c=np.log10(reg.loc[piv.index, "mean_demand_mw"]), cmap="viridis")
    cb = fig.colorbar(sc, ax=ax, fraction=0.05, pad=0.02)
    cb.set_label("log$_{10}$ mean demand (MW)")
    ax.plot([0, mx], [0, mx], "k--", lw=0.7)
    ax.set_xlabel("nMAE, global in-region (%)")
    ax.set_ylabel("nMAE, global unseen region (%)")
    ax.set_title("h = 24 h", loc="left")
    top = piv.LGB_G_IN.sort_values().index[-3:]
    for k, r in enumerate(top):
        ax.annotate(r, (piv.loc[r, "LGB_G_IN"], piv.loc[r, "LGB_G_LRO"]), fontsize=7, xytext=(-28, 6 + 4 * k),
                    textcoords="offset points", arrowprops=dict(arrowstyle="-", lw=0.4))
    panel_label(ax, "(a)")
    ax = axes[1]
    for hh, mk in zip(sorted(pr.h.unique()), ["o", "s", "^"]):
        p = pr[pr.h == hh].pivot(index="region", columns="method", values="nMAE")
        gap = (p.LGB_G_LRO / p.LGB_G_IN - 1) * 100
        ax.scatter(reg.loc[p.index, "mean_demand_mw"], gap, s=12, marker=mk, label=f"h = {hh} h", alpha=0.8)
        for r in gap.index[gap > 15]:
            ax.annotate(r, (reg.loc[r, "mean_demand_mw"], gap[r]), fontsize=7, xytext=(4, -2), textcoords="offset points")
    ax.axhline(0, color="k", lw=0.7)
    ax.set_xscale("log")
    ax.set_xlabel("Mean demand (MW, log scale)")
    ax.set_ylabel("Geographic gap: unseen vs in-region (%)")
    ax.legend(frameon=False)
    panel_label(ax, "(b)")
    fig.tight_layout()
    save(fig, "fig06_regional_errors", "(a) Per-BA nMAE of the global model when the BA is held out vs included in "
         "training (colour: log10 mean demand). (b) Relative geographic generalisation gap vs BA size.",
         "results/metrics/point_metrics_by_region.csv; data/processed/regions.csv")


# ----------------------------------------------------------------------------- 7 temporal
def fig_temporal():
    s = pd.read_csv(METRIC_DIR / "temporal_metrics_summary.csv")
    r = pd.read_csv(METRIC_DIR / "refit_metrics_summary.csv")
    fig, axes = plt.subplots(1, 3, figsize=(W2, 2.8), gridspec_kw={"width_ratios": [1, 1, 1]})
    yr = s[s.by == "year"]
    periods = ["2023 (validation)", "2024", "2025"]
    for m in ["SN24", "LGB_L", "LGB_G_IN", "LGB_G_LRO"]:
        d = yr[(yr.h == 24) & (yr.method == m)].set_index("period").reindex(periods)
        axes[0].plot(range(3), d.nMAE_median * 100, marker="o", color=C[m], label=LAB[m], ms=4)
    axes[0].set_xticks(range(3), ["2023\n(val.)", "2024", "2025"])
    axes[0].set_ylabel("Median nMAE (%)")
    axes[0].set_title("Drift, h = 24 h", loc="left")
    axes[0].legend(frameon=False, fontsize=7)
    panel_label(axes[0], "(a)")
    se = s[(s.by == "season") & (s.h == 24)]
    seasons = ["DJF", "MAM", "JJA", "SON"]
    for i, (m, mk) in enumerate(zip(["LGB_L", "LGB_G_IN", "LGB_G_LRO"], ["s", "o", "^"])):
        d = se[se.method == m].set_index("period").reindex(seasons)
        axes[1].plot(np.arange(4) + (i - 1) * 0.12, d.nMAE_median * 100, ls="none", marker=mk, ms=6,
                     color=C[m], label=LAB[m])
    axes[1].set_xticks(range(4), seasons)
    axes[1].set_xlim(-0.5, 3.5)
    axes[1].set_title("Season, h = 24 h", loc="left")
    axes[1].legend(frameon=False, fontsize=7, loc="lower left")
    panel_label(axes[1], "(b)")
    hs = sorted(r.h.unique())
    x = np.arange(len(hs))
    for i, (m, lab, c) in enumerate([("LGB_G_IN", "global frozen", C["LGB_G_IN"]),
                                     ("LGB_G_IN_refit", "global refit", "#003F66"),
                                     ("LGB_L", "local frozen", C["LGB_L"]), ("LGB_L_refit", "local refit", "#8A5F00")]):
        d = r[r.method == m].set_index("h").reindex(hs)
        axes[2].bar(x + (i - 1.5) * 0.2, d.nMAE_median * 100, width=0.2, color=c, label=lab)
    axes[2].set_xticks(x, [f"{h} h" for h in hs])
    axes[2].set_title("Refit on 2025", loc="left")
    axes[2].set_ylim(0, 6.2)
    axes[2].legend(frameon=False, fontsize=6.5, ncol=2, loc="upper left")
    panel_label(axes[2], "(c)")
    fig.tight_layout()
    save(fig, "fig08_temporal_shift", "Temporal distribution shift: (a) median nMAE by year for models trained on "
         "2019–2022; (b) by season (test period); (c) frozen vs refit models on 2025.",
         "results/metrics/temporal_metrics_summary.csv; results/metrics/refit_metrics_summary.csv")


# ----------------------------------------------------------------------------- 8 transfer
def fig_transfer():
    s = pd.read_csv(METRIC_DIR / "adaptation_metrics_summary.csv")
    hs = sorted(s.h.unique())
    fig, axes = plt.subplots(1, len(hs), figsize=(W2, 2.8), sharey=False)
    ks = [1, 4, 13]
    for ax, h in zip(axes, hs):
        d = s[s.h == h].set_index("method")
        zero = d.loc["LGB_G_LRO", "nMAE_median"] * 100
        ft = [zero] + [d.loc[f"LGB_FT_k{k}", "nMAE_median"] * 100 for k in ks]
        lo = [d.loc[f"LGB_L_k{k}", "nMAE_median"] * 100 for k in ks]
        ax.plot([0] + ks, ft, marker="o", color=C["FT"], label="global + fine-tune", ms=4)
        ax.plot(ks, lo, marker="s", color=C["LOC"], label="local, k weeks only", ms=4)
        ax.axhline(d.loc["LGB_G_IN", "nMAE_median"] * 100, color=C["LGB_G_IN"], ls="--", lw=0.9, label="global in-region (4 yr)")
        ax.axhline(d.loc["LGB_L", "nMAE_median"] * 100, color=C["LGB_L"], ls=":", lw=1.1, label="local (4 yr)")
        ax.scatter([0], [zero], color=C["LGB_G_LRO"], zorder=3, s=25, label="zero-shot global")
        ax.set_xscale("symlog", linthresh=1)
        ax.set_xticks([0, 1, 4, 13], ["0", "1", "4", "13"])
        ax.set_xlabel("Target data (weeks)")
        ax.set_title(f"h = {h} h", loc="left")
    axes[0].set_ylabel("Median nMAE (%)")
    axes[-1].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    save(fig, "fig07_transfer", "Limited target-data adaptation for unseen BAs: median test nMAE vs weeks of target (x-axis on a symmetric-log scale) "
         "history.", "results/metrics/adaptation_metrics_summary.csv")


# ----------------------------------------------------------------------------- 9 calibration
def fig_calibration():
    pr = pd.read_csv(METRIC_DIR / "probabilistic_by_region.csv")
    mon = pd.read_csv(METRIC_DIR / "probabilistic_monthly_coverage.csv")
    meths = ["QR", "SCP", "CQR", "SCP-T4", "ACI-CQR", "ACI-CQR-V"]
    fig, axes = plt.subplots(1, 3, figsize=(W2, 3.0), gridspec_kw={"width_ratios": [1.1, 1.1, 1.2]})
    d0 = pr[(pr.alpha == 0.1) & (pr.period == "all") & (pr.h == 24)]
    rng = np.random.default_rng(0)
    for ax, setting in zip(axes[:2], ["in-region", "unseen-region"]):
        for i, m in enumerate(meths):
            v = d0[(d0.setting == setting) & (d0.method == m)].coverage * 100
            ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=6, alpha=0.6, color="#0072B2")
            ax.plot([i - 0.3, i + 0.3], [v.mean()] * 2, color="k", lw=1.2)
        ax.axhline(90, color="#D55E00", ls="--", lw=0.9)
        ax.set_xticks(range(len(meths)), meths, rotation=45, ha="right")
        ax.set_title(f"{setting}, h = 24 h", loc="right", fontsize=9.5)
    axes[0].set_ylabel("Empirical coverage of 90% interval (%)")
    lo = min(axes[0].get_ylim()[0], axes[1].get_ylim()[0])
    for ax in axes[:2]:
        ax.set_ylim(lo, 100.5)
    panel_label(axes[0], "(a)")
    panel_label(axes[1], "(b)")
    ax = axes[2]
    mm = mon[(mon.alpha == 0.1) & (mon.h == 24) & (mon.setting == "unseen-region")]
    for m, c in zip(meths, ["#999999", "#CC79A7", "#0072B2", "#E69F00", "#56B4E9", "#009E73"]):
        d = mm[mm.method == m].sort_values("month")
        ax.plot(pd.PeriodIndex(d.month, freq="M").to_timestamp(), d.coverage * 100, color=c, lw=1, label=m)
    ax.axhline(90, color="#D55E00", ls="--", lw=0.9)
    ax.set_ylabel("Pooled monthly coverage (%)")
    ax.set_title("unseen-region, by month", loc="right", fontsize=9.5)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b\n%Y"))
    ax.legend(frameon=False, fontsize=6.5, ncol=2)
    panel_label(ax, "(c)")
    fig.tight_layout()
    save(fig, "fig09_calibration", "Calibration of nominal 90% intervals (h = 24 h): per-BA coverage (dots; bar = mean) "
         "for (a) in-region and (b) unseen-region models; (c) monthly pooled coverage for unseen BAs.",
         "results/metrics/probabilistic_by_region.csv; results/metrics/probabilistic_monthly_coverage.csv")


# ----------------------------------------------------------------------------- 10 intervals example
def fig_intervals(cfg, region=None):
    h = 24
    p = pd.read_parquet(PRED_DIR / f"point_h{h}.parquet")
    cal = pd.read_parquet(PRED_DIR / f"lro_source_calibration_h{h}.parquet")
    pr = pd.read_csv(METRIC_DIR / "probabilistic_by_region.csv")
    if region is None:  # BA whose unseen-region CQR coverage is closest to the cross-BA median
        d = pr[(pr.method == "CQR") & (pr.setting == "unseen-region") & (pr.h == h) & (pr.alpha == 0.1) & (pr.period == "all")]
        region = d.iloc[(d.coverage - d.coverage.median()).abs().argsort()].region.iloc[0]
    g = p[(p.region == region) & (p.split == "test") & p.eval_ok].sort_values("time_utc")
    f = int(g.fold.iloc[0])
    cf = cal[cal.fold == f]
    zl, zu = (g.LGB_G_LRO_q05 / g.scale).to_numpy(), (g.LGB_G_LRO_q95 / g.scale).to_numpy()
    cs = cqr_scores(cf.z.to_numpy(), cf.zq05.to_numpy(), cf.zq95.to_numpy())
    q = conformal_quantile(cs, 0.1)
    gsel = pd.read_csv(METRIC_DIR / "aci_gamma_selected_on_validation.csv")
    gam = float(gsel[(gsel.h == h) & (gsel.alpha == 0.1)].gamma_selected.iloc[0])
    qa, _, _ = aci_intervals(cs, cqr_scores((g.y / g.scale).to_numpy(), zl, zu), 0.1, gam, h)
    s = g.scale.to_numpy()
    w = (g.time_utc >= "2024-07-15") & (g.time_utc < "2024-07-29")
    fig, ax = plt.subplots(figsize=(W2, 2.8))
    t = g.time_utc[w]
    ax.fill_between(t, ((zl - q) * s)[w] / 1000, ((zu + q) * s)[w] / 1000, color="#56B4E9", alpha=0.35, label="CQR 90%")
    ax.plot(t, ((zl - qa) * s)[w] / 1000, color="#009E73", lw=0.7, label=f"ACI-CQR-V 90% bounds (γ = {gam:g})")
    ax.plot(t, ((zu + qa) * s)[w] / 1000, color="#009E73", lw=0.7)
    ax.plot(t, g.LGB_G_LRO[w] / 1000, color="#0072B2", lw=0.9, label="median forecast")
    ax.plot(t, g.y[w] / 1000, color="k", lw=0.8, label="observed")
    ax.set_ylabel("Demand (GW)")
    ax.set_title(f"{region} held out from training (fold {f}), h = 24 h, 15–28 July 2024 (UTC)", loc="left", fontsize=10)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d %b"))
    ax.legend(frameon=False, ncol=4, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.15))
    fig.tight_layout()
    save(fig, "fig10_interval_example", f"Day-ahead 90% prediction intervals for an unseen BA ({region}), test period "
         "(BA chosen as the one with median CQR coverage).", f"results/predictions/point_h{h}.parquet; "
         f"results/predictions/lro_source_calibration_h{h}.parquet")


# ----------------------------------------------------------------------------- 11 missing
def fig_missing():
    s = pd.read_csv(METRIC_DIR / "missing_data_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(W2, 2.9), sharey=False)
    rates = {"clean": 0, "MCAR_5": 5, "MCAR_10": 10, "MCAR_20": 20, "MCAR_40": 40}
    for ax, h in zip(axes, sorted(s.h.unique())):
        d = s[(s.h == h) & s.scenario.isin(rates)]
        for (m, st), c, ls in [(("LGB_G_IN", "native"), "#0072B2", "-"), (("LGB_G_IN", "locf"), "#0072B2", "--"),
                               (("LGB_G_IN", "seasonal"), "#0072B2", ":"), (("LGB_G_IN_AUG", "native"), "#D55E00", "-"),
                               (("LGB_G_LRO", "native"), "#56B4E9", "-")]:
            dd = d[(d.method == m) & ((d.strategy == st) | (d.scenario == "clean"))]
            dd = dd.assign(r=dd.scenario.map(rates)).sort_values("r").drop_duplicates("r")
            lab = {"LGB_G_IN": "global in", "LGB_G_IN_AUG": "global in, MCAR-trained", "LGB_G_LRO": "global unseen"}[m]
            stl = {"native": "native NaN", "locf": "LOCF imputation", "seasonal": "weekly-seasonal imputation"}[st]
            ax.plot(dd.r, dd.nMAE_median * 100, color=c, ls=ls, marker="o", ms=3, label=f"{lab}, {stl}")
        for sc, mk in (("BLOCK_24h", "x"), ("BLOCK_168h", "+")):
            b = s[(s.h == h) & (s.scenario == sc) & (s.method == "LGB_G_IN") & (s.strategy == "native")]
            if len(b):
                ax.scatter(b.input_missing_share * 100, b.nMAE_median * 100, marker=mk, color="k", s=30,
                           label=f"{sc.replace('BLOCK_', 'outages ')} (global in, native)")
        ax.set_xlabel("Inputs missing (%)")
        ax.set_title(f"h = {h} h", loc="left")
    axes[0].set_ylabel("Median nMAE (%)")
    axes[1].legend(frameon=False, fontsize=6.5)
    fig.tight_layout()
    save(fig, "fig11_missing_data", "Robustness to missing inputs: median test nMAE vs share of missing input hours "
         "for imputation strategies; × and + mark 24-h and 168-h outage scenarios.",
         "results/metrics/missing_data_summary.csv")


# ----------------------------------------------------------------------------- 12 ablation
def fig_ablation():
    s = pd.read_csv(METRIC_DIR / "ablation_results.csv")
    s = s[~s.method.isin(["LGB_G_LRO"])].copy()
    pool = s[s.method.str.startswith("pool_")].copy()
    pool["n"] = pool.method.str.extract(r"pool_(\d+)").astype(int)
    rest = s[~s.method.str.startswith("pool_")]
    fig, axes = plt.subplots(1, 2, figsize=(W2, 2.7), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    y = np.arange(len(rest))
    ax.barh(y, rest.median_rel_change * 100, color="#0072B2")
    ax.errorbar(rest.median_rel_change * 100, y, xerr=[(rest.median_rel_change - rest.rel_ci_lo) * 100,
                                                       (rest.rel_ci_hi - rest.median_rel_change) * 100],
                fmt="none", color="k", lw=0.8, capsize=2)
    names = {"no_calendar": "no calendar features", "no_weekly_lags": "no weekly lags",
             "recent_lags_0_3_only": "recent lags 0–3 h only", "LGB_G_IN": "in-region model (reference)"}
    ax.set_yticks(y, [names.get(m, m) for m in rest.method])
    ax.axvline(0, color="k", lw=0.7)
    ax.set_xlabel("Median change in nMAE vs full zero-shot model (%)")
    panel_label(ax, "(a)")
    ax = axes[1]
    ax.scatter(pool.n, pool.nMAE_median * 100, color="#56B4E9", s=18, label="random source pools")
    full = s.loc[s.method == "LGB_G_IN"]
    base = pd.read_csv(METRIC_DIR / "ablation_results.csv")
    base = base[base.method == "LGB_G_LRO"].nMAE_median.iloc[0] * 100
    ax.scatter([40], [base], color="#0072B2", s=30, marker="D", label="all 40 sources")
    ax.set_xscale("log")
    ax.set_xticks([5, 10, 20, 40], ["5", "10", "20", "40"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("Number of source BAs")
    ax.set_ylabel("Median nMAE (%)")
    ax.legend(frameon=False, fontsize=7)
    panel_label(ax, "(b)")
    fig.tight_layout()
    save(fig, "fig12_ablation", "Ablations of the zero-shot global model (h = 24 h): (a) feature groups (bars: median "
         "relative change; whiskers: 95% bootstrap CI over BAs); (b) size of the source-region pool.",
         "results/metrics/ablation_results.csv")


# ----------------------------------------------------------------------------- 13 compute
def fig_compute():
    c = pd.read_csv(LOG_DIR / "compute_costs_point.csv")
    c = c[~c.model.str.contains("_q")]
    g = c.groupby(["model", "h"]).agg(fit=("fit_seconds", "mean"), size=("size_bytes", "mean")).reset_index()
    a = pd.read_csv(LOG_DIR / "compute_costs_adapt.csv")
    fig, axes = plt.subplots(1, 2, figsize=(W2, 2.7))
    models = ["RIDGE_G_IN", "LGB_L (48 models)", "LGB_G_IN", "LGB_G_LRO"]
    labels = ["Ridge\nglobal", "LightGBM\nlocal (48)", "LightGBM\nglobal", "LightGBM\nLRO (per fold)"]
    hs = sorted(g.h.unique())
    for i, h in enumerate(hs):
        d = g[g.h == h].set_index("model").reindex(models)
        axes[0].bar(np.arange(len(models)) + (i - 1) * 0.26, d.fit, width=0.26, label=f"h = {h} h")
        dd = d.dropna(subset=["size"])
        axes[1].bar(np.arange(len(models)) + (i - 1) * 0.26, d["size"] / 1e6, width=0.26, label=f"h = {h} h")
    for ax in axes:
        ax.set_xticks(range(len(models)), labels, fontsize=7.5)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Training time (s, log)")
    axes[1].set_ylabel("Serialized model size (MB)")
    axes[0].legend(frameon=False, fontsize=7)
    ft = a[a.model.str.startswith("LGB_FT")].fit_seconds_per_region.mean()
    axes[0].text(0.02, 0.97, f"fine-tuning: {ft:.2f} s per BA (mean)", transform=axes[0].transAxes, va="top", fontsize=7.5)
    panel_label(axes[0], "(a)")
    panel_label(axes[1], "(b)")
    fig.tight_layout()
    save(fig, "fig13_compute", "Computational cost on a 4-core CPU: (a) wall-clock training time; (b) serialised model "
         "size (ridge size not measured). The h = 6 h in-region fit coincided with a concurrent evaluation job and its time "
         "is inflated by CPU contention; LRO fits at h = 6 h are representative.", "results/logs/compute_costs_point.csv; results/logs/compute_costs_adapt.csv")


def main():
    cfg = load_config()
    fns = [fig_workflow, fig_coverage, fig_series, fig_quality, fig_accuracy, fig_regions, fig_temporal,
           fig_transfer, fig_calibration, lambda: fig_intervals(cfg), fig_missing, fig_ablation, fig_compute]
    for fn in fns:
        try:
            fn()
        except FileNotFoundError as e:
            print(f"skip: {e}")
    pd.DataFrame(MANIFEST).to_csv(FIG_DIR / "figure_manifest.csv", index=False)
    print(f"font used: {FONT}; {len(MANIFEST)} figures")


if __name__ == "__main__":
    main()
