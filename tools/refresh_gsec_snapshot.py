#!/usr/bin/env python3
"""Refresh the GSEC Analyzer snapshot embedded in web/index.html, then copy it to index.html.

gsec.rabbyz.com sends no CORS headers, so the page cannot read it live; this pulls
its public API and rewrites the five `const GS_* = ...;` lines in the page script.

    python tools/refresh_gsec_snapshot.py            # rewrite both pages
    python tools/refresh_gsec_snapshot.py --dry-run  # print what it would embed
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

API = "https://gsec.rabbyz.com/api"
ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "index.html"
ROWS = 24  # bonds on the scrolling board, spread evenly by maturity
YAS_ISIN = "BD0935291106"  # 10Y BGTB 22/01/2035, the bond in the YAS panel


def get(path: str) -> dict:
    req = urllib.request.Request(API + path, headers={"User-Agent": "rabbyz-site-refresh"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def row(b: dict) -> list:
    name = b["name"].replace(" BGTB", "").replace("/20", "/")
    return [b["isin"], name, b["coupon_pct"], round(b["market_yield_pct"], 4), round(b["market_price"], 4),
            round(b["chg_bp"] or 0, 1), round(b["remaining_years"], 2), b["type"]]


def snapshot() -> dict[str, object]:
    bonds = get("/bonds")
    priced = sorted((b for b in bonds["bonds"] if b.get("market_yield_pct") and b.get("market_price")),
                    key=lambda b: b["remaining_years"])
    step = len(priced) / ROWS
    board = [row(priced[int(i * step)]) for i in range(ROWS)]
    yas = next((b for b in priced if b["isin"] == YAS_ISIN), priced[len(priced) * 2 // 3])

    dates = get("/curve/dates")["dates"]
    curve = get(f"/curve?date={dates[0]}")
    prev = get(f"/curve?date={dates[1]}")
    pts = lambda c: [[p["tenor"], p["yield_pct"]] for p in c["points"]]
    return {
        "GS_META": {"date": bonds["date"], "curve": curve["date"], "prev": prev["date"]},
        "GS_BONDS": board,
        "GS_YAS": row(yas),
        "GS_CURVE": pts(curve),
        "GS_PREV": pts(prev),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    snap = snapshot()
    if args.dry_run:
        print(json.dumps(snap["GS_META"]), len(snap["GS_BONDS"]), "bonds,", len(snap["GS_CURVE"]), "curve points")
        return 0

    html = PAGE.read_text(encoding="utf-8")
    for name, value in snap.items():
        line = f"    const {name} = {json.dumps(value, separators=(',', ':'))};"
        html, n = re.subn(rf"^    const {name} = .*;$", lambda _: line, html, count=1, flags=re.M)
        if n != 1:
            print(f"ERROR: `const {name} = ...;` not found in {PAGE}", file=sys.stderr)
            return 1
    PAGE.write_text(html, encoding="utf-8", newline="\n")
    shutil.copyfile(PAGE, ROOT / "index.html")
    print("refreshed:", json.dumps(snap["GS_META"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
