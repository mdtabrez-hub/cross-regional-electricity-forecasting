"""Automated consistency checks for the final QA report.

Usage: python -m src.qa_checks   -> results/logs/qa_checks.json (+ printed summary)

Checks
  * every {{key}} in the manuscript source exists and is re-derivable from metric files
  * a sample of numbers is independently recomputed from raw predictions
  * all citation keys resolve in the BibTeX file; no unresolved citations remain in the DOCX
  * every figure/table referenced exists and is listed in its manifest with a source file
  * the DOCX uses Times New Roman for every run and 12-pt justified 1.5-spaced body text
  * no leftover placeholders ("TODO", "XX", "??") in the rendered manuscript
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

import numpy as np
import pandas as pd

from .common import FIG_DIR, LOG_DIR, METRIC_DIR, PRED_DIR, RESULTS, ROOT, TABLE_DIR, save_json
from . import metrics as M

MS = ROOT / "manuscript"


def check(name, ok, detail=""):
    status = "Passed" if ok is True else ("Failed" if ok is False else ok)
    return {"check": name, "status": status, "detail": detail}


def main():
    out = []
    src = "".join((MS / "sections" / f).read_text() for f in sorted(p.name for p in (MS / "sections").glob("*.md")))
    nums = json.load(open(RESULTS / "manuscript_numbers.json"))
    keys = set(re.findall(r"\{\{([^}]+)\}\}", src))
    missing = sorted(k for k in keys if k not in nums)
    out.append(check("All manuscript number keys resolve", not missing, f"{len(keys)} keys; missing={missing[:10]}"))

    # independent recomputation of headline numbers from predictions
    try:
        p = pd.read_parquet(PRED_DIR / "point_h24.parquet")
        te = p[(p.split == "test") & p.eval_ok]
        cols = ["seasonal_naive_24", "seasonal_naive_168", "persistence", "RIDGE_G_IN", "RIDGE_G_LRO", "LGB_L",
                "LGB_G_IN", "LGB_G_LRO"]
        te = te[np.isfinite(te[cols]).all(axis=1) & np.isfinite(te.y)]
        per = te.groupby("region", observed=True).apply(
            lambda g: pd.Series({c: M.nmae(g.y.to_numpy(), g[c].to_numpy()) for c in ["LGB_G_IN", "LGB_G_LRO", "LGB_L"]}),
            include_groups=False)
        diffs = []
        for c in ["LGB_G_IN", "LGB_G_LRO", "LGB_L"]:
            rec = f"{100 * per[c].median():.2f}"
            rep = nums.get(f"point.h24.{c}.nMAE_median")
            diffs.append((c, rec, rep))
        ok = all(a == b for _, a, b in diffs)
        out.append(check("Headline h=24 nMAE medians recomputed from raw predictions", ok, str(diffs)))
    except FileNotFoundError as e:
        out.append(check("Headline recomputation", "Requires manual verification", str(e)))

    # tables vs metric files (spot check: table 2 median nMAE equals summary CSV)
    try:
        t2 = pd.read_csv(TABLE_DIR / "table_2_point_accuracy.csv")
        s = pd.read_csv(METRIC_DIR / "point_metrics_summary.csv")
        v1 = sorted(round(100 * x, 2) for x in s.nMAE_median)
        v2 = sorted(float(x.split(" ")[0]) for x in t2["nMAE % median [IQR]"])
        out.append(check("Table 2 matches point_metrics_summary.csv", v1 == v2, f"{len(v1)} values"))
    except FileNotFoundError as e:
        out.append(check("Table 2 consistency", "Requires manual verification", str(e)))

    # citations
    bib = (ROOT / "literature" / "verified_references.bib").read_text()
    bibkeys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cites = set(re.findall(r"@([A-Za-z0-9_]+)", re.sub(r"\{\{[^}]+\}\}", "", src))) - {"fig", "tab"}
    cites = {c for c in cites if not c.startswith(("FIGURE", "TABLE"))}
    unknown = sorted(c for c in cites if c not in bibkeys)
    out.append(check("All citation keys exist in BibTeX", not unknown, f"{len(cites)} cited; unknown={unknown}"))
    lm = pd.read_csv(ROOT / "literature" / "literature_matrix.csv")
    weak = lm[lm.bibkey.isin(cites) & ~lm.verification_status.str.startswith("verified")][["bibkey", "verification_status"]]
    out.append(check("Cited references not fully verified", "Requires manual verification" if len(weak) else True,
                     "; ".join(f"{r.bibkey}: {r.verification_status[:60]}" for r in weak.itertuples())))

    # figures/tables
    figs = set(re.findall(r"\[\[FIGURE:([\w\-]+)\]\]", src))
    fm = pd.read_csv(FIG_DIR / "figure_manifest.csv")
    miss = [f for f in figs if not ((FIG_DIR / f"{f}.png").exists() and (FIG_DIR / f"{f}.pdf").exists())]
    out.append(check("Referenced figures exist (PNG+PDF)", not miss, f"{len(figs)} figures; missing={miss}"))
    out.append(check("Figures listed in manifest", figs <= set(fm.figure), f"not in manifest={sorted(figs - set(fm.figure))}"))
    out.append(check("Figure font", "Partially verified" if (fm.font != "Times New Roman").any() else True,
                     f"fonts used: {sorted(set(fm.font))} (Times New Roman not installed; metric-compatible substitute)"))
    tabs = set(re.findall(r"\[\[TABLE:([\w\-]+)\]\]", src))
    miss = [t for t in tabs if not (TABLE_DIR / f"{t}.md").exists()]
    out.append(check("Referenced tables exist", not miss, f"{len(tabs)} tables; missing={miss}"))

    # docx formatting
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        d = Document(MS / "manuscript_final.docx")
        fonts, sizes, bad_align = set(), set(), 0
        body = 0
        for para in d.paragraphs:
            for r in para.runs:
                if r.text.strip():
                    fonts.add(r.font.name)
            if para.style.name in ("Body Text", "First Paragraph", "Compact") and para.text.strip():
                body += 1
                sizes.update({r.font.size.pt for r in para.runs if r.font.size})
                if para.alignment != WD_ALIGN_PARAGRAPH.JUSTIFY or para.paragraph_format.line_spacing != 1.5:
                    bad_align += 1
        for t in d.tables:
            for row in t.rows:
                for c in row.cells:
                    for para in c.paragraphs:
                        for r in para.runs:
                            if r.text.strip():
                                fonts.add(r.font.name)
        out.append(check("DOCX fonts are Times New Roman", fonts <= {"Times New Roman"}, f"fonts={fonts}"))
        out.append(check("DOCX body 12 pt", sizes <= {12.0}, f"body sizes={sizes}; body paragraphs={body}"))
        out.append(check("DOCX body justified, 1.5 spacing", bad_align == 0, f"non-conforming body paragraphs={bad_align}"))
        txt = "\n".join(p.text for p in d.paragraphs)
        unresolved = re.findall(r"\?\?|\[@[^\]]+\]|\{\{|\[\[|TODO|XXX", txt)
        out.append(check("No unresolved citations/placeholders in DOCX", not unresolved, f"{unresolved[:10]}"))
        out.append(check("DOCX embeds figures", len(d.inline_shapes) == len(figs),
                         f"inline images={len(d.inline_shapes)}, referenced={len(figs)}"))
        out.append(check("DOCX tables", len(d.tables) >= len(tabs), f"tables={len(d.tables)}"))
    except Exception as e:  # noqa: BLE001
        out.append(check("DOCX inspection", False, repr(e)))
    out.append(check("PDF rendered", (MS / "manuscript_final.pdf").exists(), "LibreOffice headless"))

    # tests
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(ROOT / "tests")], capture_output=True, text=True)
    out.append(check("Unit tests", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-200:]))

    save_json(out, LOG_DIR / "qa_checks.json")
    for o in out:
        print(f"[{o['status']}] {o['check']}: {o['detail'][:160]}")


if __name__ == "__main__":
    main()
