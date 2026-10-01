#!/usr/bin/env python3
"""Where do my beliefs beat the price? — AGENT-EDITABLE (strategy/tools/).

Read-only audit over journal/forecasts.jsonl and journal/ledger.jsonl.
It replaces the hand-written category re-ranks in the deep retro (DEEP-
2026-09-16/17/26) with one command whose numbers carry their own noise
estimate, and it answers the standing blend-bar ask (proposals.md,
2026-09-11) with a held-out check and a leave-one-out check instead of a
single in-sample w_opt.

Sections:
  skill     per category FAMILY (the tag up to the first '-', so
            econ-cpi/econ-jobs/... pool into econ): n, mean dBrier
            (est - market mid, negative = I beat the market), and a
            t-stat. |t| < 2 is noise whatever the sign.
  disagree  dBrier by |est - mid|: where in the disagreement range my
            beliefs add or lose information.
  shrink    est' = mid + k * (est - mid). The k that minimises Brier on
            the first half of settled rows (by record time), scored on
            the second half, and vice versa. A k that is stable across
            halves and well below 1 means: my raw disagreement is
            mostly noise, and only ~k of it is signal.
  blend     the score.py blend bar on the disagreement slice
            (|est - mid| >= 0.05): w_opt, improvement vs market, and the
            improvement after dropping the single most helpful row.
            Rows need a two-sided book and must not be superseded, so n and
            w_opt differ slightly from score.py's blend line.
  bets      settled ledger bets by claimed edge band and entry price band.

Usage: python3 strategy/tools/edge_audit.py [--section NAME ...] [--min-n N]
       [--json]
"""
import argparse
import json
import math
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
FORECASTS = ROOT / "journal" / "forecasts.jsonl"
LEDGER = ROOT / "journal" / "ledger.jsonl"
SECTIONS = ("skill", "disagree", "shrink", "blend", "bets")


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def settled_forecasts():
    """Settled, non-superseded rows with a two-sided book, record-time order."""
    out = []
    for r in load(FORECASTS):
        if r.get("status") not in ("won", "lost") or r.get("superseded_by"):
            continue
        if r.get("best_ask_at_record") is None or r.get("best_bid_at_record") is None:
            continue
        r["_y"] = 1.0 if r["status"] == "won" else 0.0
        # same market baseline as score.py: the recorded mid, else bid/ask
        m = r.get("market_prob_at_record")
        r["_mid"] = m if m is not None else (r["best_ask_at_record"] + r["best_bid_at_record"]) / 2
        out.append(r)
    out.sort(key=lambda r: (r["ts"], r["id"]))
    return out


def dbrier(r, k=1.0):
    est = r["_mid"] + k * (r["est_prob"] - r["_mid"])
    return (est - r["_y"]) ** 2 - (r["_mid"] - r["_y"]) ** 2


def mean_t(xs):
    n = len(xs)
    m = sum(xs) / n
    if n < 2:
        return m, 0.0
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def skill(rows, min_n):
    fam = defaultdict(list)
    for r in rows:
        fam[(r.get("category") or "?").split("-")[0]].append(dbrier(r))
    out = []
    for f, xs in fam.items():
        if len(xs) < min_n:
            continue
        m, t = mean_t(xs)
        verdict = "beats market" if t <= -2 else "worse than market" if t >= 2 else "noise"
        out.append({"family": f, "n": len(xs), "dbrier": round(m, 4),
                    "t": round(t, 2), "verdict": verdict})
    return sorted(out, key=lambda x: x["t"])


def disagree(rows):
    edges = [(0.0, 0.02), (0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 1.01)]
    out = []
    for lo, hi in edges:
        xs = [dbrier(r) for r in rows if lo <= abs(r["est_prob"] - r["_mid"]) < hi]
        if xs:
            m, t = mean_t(xs)
            out.append({"abs_diff": f"{lo:.2f}-{hi:.2f}", "n": len(xs),
                        "dbrier": round(m, 4), "t": round(t, 2)})
    return out


def best_k(rows):
    grid = [i / 20 for i in range(21)]
    return min(grid, key=lambda k: sum(dbrier(r, k) for r in rows))


def shrink(rows):
    h = len(rows) // 2
    a, b = rows[:h], rows[h:]
    out = {}
    for name, fit_on, test_on in (("fit_first_test_second", a, b),
                                  ("fit_second_test_first", b, a)):
        k = best_k(fit_on)
        n = len(test_on)
        out[name] = {
            "k": k, "n_test": n,
            "test_dbrier_shrunk": round(sum(dbrier(r, k) for r in test_on) / n, 5),
            "test_dbrier_raw": round(sum(dbrier(r) for r in test_on) / n, 5),
        }
    out["k_all"] = best_k(rows)
    return out


def blend(rows):
    """score.py's blend on |est - mid| >= 0.05, plus leave-one-out."""
    d = [(r["est_prob"], r["_mid"], r["_y"], r["id"]) for r in rows
         if abs(r["est_prob"] - r["_mid"]) >= 0.05]
    if len(d) < 2:
        return {"n": len(d)}

    def fit(sl):
        # least-squares w for w*m + (1-w)*e on the blend line
        num = sum((e - y) * (e - m) for e, m, y, _ in sl)
        den = sum((e - m) ** 2 for e, m, y, _ in sl)
        w = num / den if den else 1.0
        n = len(sl)
        bm = sum((m - y) ** 2 for e, m, y, _ in sl) / n
        bb = sum((w * m + (1 - w) * e - y) ** 2 for e, m, y, _ in sl) / n
        return w, bm - bb

    w, imp = fit(d)
    loo = []
    for i in range(len(d)):
        _, imp_i = fit(d[:i] + d[i + 1:])
        loo.append((imp_i, d[i][3]))
    worst_imp, worst_id = min(loo)
    return {"n": len(d), "w_opt": round(w, 3), "improvement": round(imp, 4),
            "loo_min_improvement": round(worst_imp, 4), "loo_drop_id": worst_id,
            "bar_0.002_survives_loo": worst_imp >= 0.002 and w <= 0.80}


def bets():
    s = [r for r in load(LEDGER) if r.get("status") in ("won", "lost")]

    def band(x, cuts):
        for lo, hi in cuts:
            if lo <= x < hi:
                return f"{lo:.2f}-{hi:.2f}"
        return "other"

    edge_cuts = [(-1, 0.04), (0.04, 0.07), (0.07, 0.10), (0.10, 0.20), (0.20, 2)]
    px_cuts = [(0, 0.20), (0.20, 0.45), (0.45, 0.70), (0.70, 0.90), (0.90, 1.01)]
    out = {}
    for name, key, cuts in (("by_claimed_edge", lambda r: r["est_prob"] - r["entry_price"], edge_cuts),
                            ("by_entry_price", lambda r: r["entry_price"], px_cuts)):
        agg = defaultdict(lambda: {"n": 0, "won": 0, "staked": 0.0, "pnl": 0.0})
        for r in s:
            a = agg[band(key(r), cuts)]
            a["n"] += 1
            a["won"] += r["status"] == "won"
            a["staked"] += r["stake_usd"]
            a["pnl"] += r.get("pnl_usd") or 0.0
        out[name] = {k: {**v, "pnl": round(v["pnl"], 2),
                         "roi": round(v["pnl"] / v["staked"], 3) if v["staked"] else 0.0}
                     for k, v in sorted(agg.items())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", action="append", choices=SECTIONS)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    want = a.section or list(SECTIONS)
    rows = settled_forecasts()
    rep = {"n_forecasts": len(rows)}
    if "skill" in want:
        rep["skill"] = skill(rows, a.min_n)
    if "disagree" in want:
        rep["disagree"] = disagree(rows)
    if "shrink" in want:
        rep["shrink"] = shrink(rows)
    if "blend" in want:
        rep["blend"] = blend(rows)
    if "bets" in want:
        rep["bets"] = bets()
    if a.json:
        print(json.dumps(rep, indent=1))
        return

    print(f"settled forecasts with a book: {rep['n_forecasts']}  "
          "(dBrier < 0 = my belief beat the market mid)")
    if "skill" in rep:
        print(f"\nskill by category family (n >= {a.min_n}; |t| < 2 is noise):")
        for x in rep["skill"]:
            print(f"  {x['family']:<14} n={x['n']:>4} dBrier={x['dbrier']:+.4f} "
                  f"t={x['t']:+.2f}  {x['verdict']}")
    if "disagree" in rep:
        print("\ndBrier by |est - mid|:")
        for x in rep["disagree"]:
            print(f"  {x['abs_diff']:<10} n={x['n']:>4} dBrier={x['dbrier']:+.4f} t={x['t']:+.2f}")
    if "shrink" in rep:
        sh = rep["shrink"]
        print(f"\nshrinkage est' = mid + k*(est - mid); k on all rows = {sh['k_all']}")
        for name in ("fit_first_test_second", "fit_second_test_first"):
            x = sh[name]
            print(f"  {name}: k={x['k']}  held-out dBrier shrunk={x['test_dbrier_shrunk']:+.5f} "
                  f"raw={x['test_dbrier_raw']:+.5f} (n={x['n_test']})")
    if "blend" in rep:
        b = rep["blend"]
        if b.get("n", 0) >= 2:
            print(f"\nblend bar (|est-mid| >= 0.05): n={b['n']} w_opt={b['w_opt']} "
                  f"improvement={b['improvement']:+.4f}  leave-one-out min="
                  f"{b['loo_min_improvement']:+.4f} (drop {b['loo_drop_id']})  "
                  f"bar survives LOO: {b['bar_0.002_survives_loo']}")
    if "bets" in rep:
        for name, tab in rep["bets"].items():
            print(f"\nsettled bets {name.replace('_', ' ')}:")
            for k, v in tab.items():
                print(f"  {k:<11} n={v['n']:>3} won={v['won']:>3} staked=${v['staked']:>6.2f} "
                      f"pnl=${v['pnl']:>+7.2f} roi={v['roi']:+.3f}")


if __name__ == "__main__":
    main()
