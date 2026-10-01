#!/usr/bin/env python3
"""Run a small live pilot against Jev to verify fit for one concrete decision.

Standard library only (urllib). Needs TYPESAFE_API_KEY in the environment, or
OPENROUTER_API_KEY with --openrouter (OpenRouter serves Jev on its own
POST /api/alpha/decisions endpoint with the same request and response shape;
model id "typesafe/jev-1.13"; no waitlist). The same OpenRouter endpoint serves
other decision models with the same request body (e.g. "liquid/d1",
"inception/mercury-decide:free"); set "model" in the spec to pilot one of them.
Reads a JSON spec that holds the questions and a list of sample states, sends
each state (optionally several times), and reports:

  - per-question answer distributions (choice counts, score/noul histograms,
    confidence quartiles) so you can see whether the model is decisive on your data
  - agreement with expected labels when the spec provides them
  - repeat stability when --repeats > 1 (does the same state get the same answer?)
  - measured latency p50/p95 and token usage, so cost estimates rest on data

Spec format (JSON):
{
  "model": "jev-latest",                       # optional
  "questions": { "<id>": {"type": "noul"|"choice"|"score", "instructions": "...", "criteria": ...}, ... },
  "samples": [
    { "state": <string|object|array>, "expected": { "<id>": "<option>"|true|false|<level int> } },   # expected is optional
    ...
  ]
}

Usage:
  python3 probe.py spec.json                # one pass
  python3 probe.py spec.json --repeats 3    # stability check
  python3 probe.py spec.json --json out.json
  OPENROUTER_API_KEY=... python3 probe.py spec.json --openrouter

Keep the pilot honest: use real, recent, messy inputs; include boundary cases and
some inputs where the right answer is "none of the above"; and look at
the wrong answers one by one before trusting an aggregate number.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request

API_URL = os.environ.get("TYPESAFE_API_URL", "https://api.typesafe.ai/v1/systemone")
OPENROUTER_URL = "https://openrouter.ai/api/alpha/decisions"


def call(api_key: str, model: str, state, questions: dict, timeout: float, url: str = API_URL) -> tuple[dict, float]:
    body = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = json.load(r)
            return data, (time.perf_counter() - t0) * 1000
        except urllib.error.HTTPError as e:
            if e.code in (429, 529) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            detail = e.read().decode(errors="replace")[:500]
            raise SystemExit(f"HTTP {e.code} from {url}: {detail}")
    raise SystemExit("gave up after retries")


def pct(values, q):
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * q
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("spec")
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--timeout", type=float, default=30.0)
    p.add_argument("--json", help="write full results to this file")
    p.add_argument("--noul-threshold", type=float, default=0.5)
    p.add_argument("--openrouter", action="store_true", help="call Jev through OpenRouter (OPENROUTER_API_KEY) instead of TypeSafe directly")
    a = p.parse_args(argv)

    if a.openrouter:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        url = OPENROUTER_URL
        if not api_key:
            print("OPENROUTER_API_KEY is not set.", file=sys.stderr)
            return 2
    else:
        api_key = os.environ.get("TYPESAFE_API_KEY")
        url = API_URL
        if not api_key:
            print("TYPESAFE_API_KEY is not set. Create a key at https://console.typesafe.ai/keys, or use --openrouter.", file=sys.stderr)
            return 2
    spec = json.load(open(a.spec))
    model = spec.get("model", "typesafe/jev-1.13" if a.openrouter else "jev-latest")
    questions = spec["questions"]
    samples = spec["samples"]

    runs = []  # (sample_idx, repeat, answers, latency_ms, usage)
    for i, s in enumerate(samples):
        for r in range(a.repeats):
            data, ms = call(api_key, model, s["state"], questions, a.timeout, url)
            runs.append((i, r, data["answers"], ms, data.get("usage", {}), data.get("model")))
            print(f"sample {i} repeat {r}: {ms:.0f} ms", file=sys.stderr)

    lat = [x[3] for x in runs]
    in_tok = [x[4].get("input_tokens", 0) for x in runs]
    costs = [x[4].get("cost") for x in runs if x[4].get("cost") is not None]
    print(f"\nModel: {runs[0][5]}   requests: {len(runs)}   samples: {len(samples)}   repeats: {a.repeats}")
    print(f"Latency ms   p50 {pct(lat, .5):.0f}   p95 {pct(lat, .95):.0f}   max {max(lat):.0f}")
    print(f"Input tokens mean {statistics.mean(in_tok):.0f}   max {max(in_tok)}   (cost/request at $0.042/Mtok: ${statistics.mean(in_tok) * 0.042 / 1e6:.6f})")
    if costs:
        print(f"Billed cost (from usage.cost): total ${sum(costs):.6f}   mean/request ${statistics.mean(costs):.6f}")

    def decided(qid, ans):
        t = questions[qid]["type"]
        if t == "noul":
            return ans["noul"] >= a.noul_threshold
        if t == "choice":
            return ans["choice"]
        return round(ans["score"])

    for qid, q in questions.items():
        t = q["type"]
        print(f"\n== {qid} ({t}): {q['instructions'] if isinstance(q['instructions'], str) else json.dumps(q['instructions'])[:120]}")
        answers = [(i, r, ans[qid]) for (i, r, ans, *_rest) in runs]
        if t == "noul":
            vals = [x[2]["noul"] for x in answers]
            bins = [0] * 5
            for v in vals:
                bins[min(int(v * 5), 4)] += 1
            print("  noul histogram [0-.2 .2-.4 .4-.6 .6-.8 .8-1]:", bins)
            mid = sum(1 for v in vals if 0.35 <= v <= 0.65)
            print(f"  in the uncertain band 0.35-0.65: {mid}/{len(vals)}")
        else:
            conf = [x[2]["confidence"] for x in answers]
            print(f"  confidence  p25 {pct(conf, .25):.2f}   p50 {pct(conf, .5):.2f}   p75 {pct(conf, .75):.2f}   below 0.5: {sum(c < 0.5 for c in conf)}/{len(conf)}")
            if t == "choice":
                counts = {}
                for x in answers:
                    counts[x[2]["choice"]] = counts.get(x[2]["choice"], 0) + 1
                print("  choice counts:", dict(sorted(counts.items(), key=lambda kv: -kv[1])))
            else:
                sc = [x[2]["score"] for x in answers]
                print(f"  score  mean {statistics.mean(sc):.2f}   min {min(sc):.2f}   max {max(sc):.2f}   levels {len(q['criteria'])}")
        # agreement with expected labels
        exp_pairs = [(x, samples[x[0]]["expected"][qid]) for x in answers if "expected" in samples[x[0]] and qid in samples[x[0]]["expected"]]
        if exp_pairs:
            ok = sum(1 for x, e in exp_pairs if decided(qid, x[2]) == e)
            print(f"  agreement with expected: {ok}/{len(exp_pairs)} = {ok / len(exp_pairs):.0%}")
            wrong = [(x[0], x[1], decided(qid, x[2]), e) for x, e in exp_pairs if decided(qid, x[2]) != e]
            for si, rep, got, e in wrong[:10]:
                print(f"    sample {si} (repeat {rep}): got {got!r}, expected {e!r}")
        # repeat stability
        if a.repeats > 1:
            by_sample = {}
            for x in answers:
                by_sample.setdefault(x[0], []).append(decided(qid, x[2]))
            flips = sum(1 for v in by_sample.values() if len(set(map(str, v))) > 1)
            print(f"  samples whose decided answer changed across repeats: {flips}/{len(by_sample)}")

    if a.json:
        out = [{"sample": i, "repeat": r, "answers": ans, "latency_ms": ms, "usage": u, "model": m} for (i, r, ans, ms, u, m) in runs]
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"\nfull results written to {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
