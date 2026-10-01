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
  python3 probe.py spec.json --validate     # offline check of the spec, no API calls
  python3 probe.py spec.json                # one pass
  python3 probe.py spec.json --repeats 3    # stability check
  python3 probe.py spec.json --json out.json
  OPENROUTER_API_KEY=... python3 probe.py spec.json --openrouter

Every run validates the spec first and stops before the first call if it finds
an error: unknown question type, too many or too few options or levels, an
expected label that is not an option, a request over the context budget, or a
question type the chosen model does not accept.

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
HERE = os.path.dirname(os.path.abspath(__file__))

# TypeSafe's published limits (docs/primitives, docs/models); per-model limits of
# rival decision models come from prices.json ("decision_models").
MAX_CHOICE_OPTIONS = 255
SCORE_LEVELS = (2, 10)
CONTEXT_TOTAL = 64_000
CONTEXT_STATE_PLUS_LONGEST_Q = 32_000
CONTEXT_OPENROUTER_JEV = 32_000  # OpenRouter serves Jev with a 32k context
CHARS_PER_TOKEN = 4  # rough English average; JSON structure adds 10-30 %


def _rough_tokens(x) -> int:
    return int(len(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)) / CHARS_PER_TOKEN) + 1


def _options(q):
    c = q.get("criteria")
    if isinstance(c, dict):
        return list(c.keys())
    if isinstance(c, list):
        return [o if isinstance(o, str) else json.dumps(o) for o in c]
    return []


def model_limits(model: str) -> dict:
    """Known per-model limits from prices.json; {} when the model is not listed."""
    try:
        dm = json.load(open(os.path.join(HERE, "prices.json"))).get("decision_models", {})
    except (OSError, ValueError):
        return {}
    for v in dm.values():
        if v.get("openrouter_id") == model or v.get("openrouter_id", "").split(":")[0] == model.split(":")[0]:
            return v
    return {}


def validate(spec: dict, model: str, openrouter: bool, repeats: int):
    """Return (errors, warnings, summary lines). Makes no network calls."""
    errors, warnings = [], []
    qs, samples = spec.get("questions"), spec.get("samples")
    if not isinstance(qs, dict) or not qs:
        errors.append('"questions" must be a non-empty object of {id: question}')
        qs = {}
    if not isinstance(samples, list) or not samples:
        errors.append('"samples" must be a non-empty list of {"state": ..., "expected": {...}}')
        samples = []
    lim = model_limits(model)
    max_opts = min(MAX_CHOICE_OPTIONS, lim.get("max_choice_options", MAX_CHOICE_OPTIONS))
    for qid, q in qs.items():
        t = q.get("type")
        if t not in ("choice", "score", "noul"):
            errors.append(f'question `{qid}`: type is {t!r}; use "choice", "score" or "noul"')
            continue
        if not q.get("instructions"):
            errors.append(f"question `{qid}`: empty instructions")
        if lim.get("noul_only") and t != "noul":
            errors.append(f"question `{qid}`: {model} accepts only Noul questions")
        if t == "choice":
            n = len(_options(q))
            if n < 2:
                errors.append(f"question `{qid}`: a Choice needs at least 2 options in `criteria`; found {n}")
            elif n > max_opts:
                who = model if max_opts < MAX_CHOICE_OPTIONS else "Jev"
                errors.append(f"question `{qid}`: {n} options; {who} accepts at most {max_opts}. Split it hierarchically or use another model")
            elif n > 240:
                warnings.append(f"question `{qid}`: {n} options; about 240 are reported reliable")
            if not any(o.lower() in ("none", "other", "allowed", "not_stated", "unknown", "none_of_the_above") for o in _options(q)):
                warnings.append(f"question `{qid}`: no none/other option; a Choice always ranks something first")
        if t == "score":
            n = len(q.get("criteria") or [])
            if not SCORE_LEVELS[0] <= n <= SCORE_LEVELS[1]:
                errors.append(f"question `{qid}`: a Score needs {SCORE_LEVELS[0]}-{SCORE_LEVELS[1]} levels in `criteria`; found {n}")
    q_tokens = {qid: _rough_tokens(q) for qid, q in qs.items()}
    longest_q = max(q_tokens.values(), default=0)
    req_tokens, labelled = [], 0
    for i, smp in enumerate(samples):
        if "state" not in smp:
            errors.append(f"sample {i}: missing \"state\"")
            continue
        st = smp["state"]
        if lim.get("noul_only") and not isinstance(st, str):
            errors.append(f"sample {i}: {model} needs the state as a string (or a conversation object)")
        st_tok = _rough_tokens(st)
        total = st_tok + sum(q_tokens.values())
        req_tokens.append(total)
        if st_tok + longest_q > CONTEXT_STATE_PLUS_LONGEST_Q:
            errors.append(f"sample {i}: state + longest question ~{st_tok + longest_q:,} tokens; the limit is {CONTEXT_STATE_PLUS_LONGEST_Q:,}. Filter or chunk the state")
        ctx = CONTEXT_OPENROUTER_JEV if (openrouter and model.startswith("typesafe/")) else CONTEXT_TOTAL
        if total > ctx:
            errors.append(f"sample {i}: request ~{total:,} tokens; the limit is {ctx:,}. Split questions or filter the state")
        elif st_tok > 8_000:
            warnings.append(f"sample {i}: state ~{st_tok:,} tokens; accuracy falls with irrelevant detail, filter first")
        exp = smp.get("expected") or {}
        if exp:
            labelled += 1
        for qid, v in exp.items():
            if qid not in qs:
                errors.append(f"sample {i}: expected label for unknown question `{qid}`; questions: {', '.join(qs)}")
                continue
            t = qs[qid].get("type")
            if t == "choice" and v not in _options(qs[qid]):
                errors.append(f"sample {i}: expected {v!r} for `{qid}` is not an option; options: {', '.join(_options(qs[qid]))}")
            elif t == "noul" and not isinstance(v, bool):
                errors.append(f"sample {i}: expected value for Noul `{qid}` must be true or false, got {v!r}")
            elif t == "score" and not (isinstance(v, int) and 0 <= v < len(qs[qid].get("criteria") or [])):
                errors.append(f"sample {i}: expected value for Score `{qid}` must be a level index 0-{len(qs[qid].get('criteria') or []) - 1}, got {v!r}")
    if samples and labelled < len(samples) / 2:
        warnings.append(f"only {labelled}/{len(samples)} samples have expected labels; label at least half")
    price = lim.get("in", 0.042)
    n_req = len(samples) * repeats
    mean_tok = statistics.mean(req_tokens) if req_tokens else 0
    summary = [f"model {model}: {len(qs)} questions, {len(samples)} samples x {repeats} repeats = {n_req} requests",
               f"~{mean_tok:,.0f} tokens per request (rough, 4 chars/token); projected cost ~${n_req * mean_tok * price / 1e6:.4f} at ${price}/M input "
               "(providers count tokens differently; the billed cost is reported after the run)"]
    return errors, warnings, summary


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
    p.add_argument("--validate", action="store_true", help="check the spec offline and print the projected cost; make no API calls")
    a = p.parse_args(argv)

    try:
        spec = json.load(open(a.spec))
    except (OSError, ValueError) as e:
        print(f"cannot read spec {a.spec}: {e}", file=sys.stderr)
        return 2
    model = spec.get("model", "typesafe/jev-1.13" if a.openrouter else "jev-latest")
    errors, warnings, summary = validate(spec, model, a.openrouter, a.repeats)
    for line in summary:
        print(line, file=sys.stderr)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        print(f"spec has {len(errors)} error(s); fix them before spending on API calls", file=sys.stderr)
        return 1
    if a.validate:
        print("spec OK" + (f" ({len(warnings)} warning(s))" if warnings else ""))
        return 0

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
