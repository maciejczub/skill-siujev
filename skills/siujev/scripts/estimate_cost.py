#!/usr/bin/env python3
"""Estimate the cost and latency of a Jev (TypeSafe System One) workload and
compare it with doing the same judgment through an LLM.

Standard library only. Prices, limits and preset latencies are read from
prices.json in this directory (dated, with a source for each latency); override
any of them on the command line. Re-check before quoting them to anyone. Run
with --list-presets to see the built-in LLM price presets by tier.

Examples
--------
  # 50k support tickets/day, ~600 tokens of state, 6 questions of ~40 tokens each
  python3 estimate_cost.py --items-per-day 50000 --state-tokens 600 \
      --questions 6 --tokens-per-question 40

  # Same, comparing against a cheap-tier LLM prompt of 900 input / 60 output tokens
  python3 estimate_cost.py --items-per-day 50000 --state-tokens 600 \
      --questions 6 --llm-input-tokens 900 --llm-output-tokens 60 \
      --llm-name deepseek-v4.1-flash

  # Any other model: give its prices explicitly
  python3 estimate_cost.py --items-per-day 50000 --state-tokens 600 --questions 6 \
      --llm-input-tokens 900 --llm-name "my-model" --llm-input-price 0.2 --llm-output-price 1.2

  # Pairwise reranking: 40 queries/day x 30 candidates, one request per query,
  # each candidate is a ~200-token entry of the state and gets one Noul
  python3 estimate_cost.py --items-per-day 40 --state-tokens 6000 --questions 30

Rough token rule of thumb when you have no measurement: 1 token ~ 4 characters of
English text; JSON keys and structure add 10-30 %.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Every price, limit and latency comes from prices.json next to this script, the
# single dated source the references cite. Edit numbers there, not here.
PRICES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json")
try:
    PRICES = json.load(open(PRICES_PATH))
except (OSError, ValueError) as e:
    sys.exit(f"cannot read {PRICES_PATH}: {e}. Restore it from the skill repository.")

_J = PRICES["jev"]
JEV_PRICE_PER_MTOK = _J["price_in"]  # USD per million input tokens; output is free
JEV_RATE_TOKENS_PER_S = _J["rate_tokens_per_s"]  # changed after launch; TypeSafe says limits adjust dynamically
JEV_RATE_REQUESTS_PER_S = _J["rate_requests_per_s"]
JEV_RATE_REQUESTS_PER_MIN = JEV_RATE_REQUESTS_PER_S * 60
JEV_CONTEXT_TOTAL = _J["context_total"]
JEV_CONTEXT_STATE_PLUS_LONGEST_Q = _J["context_state_plus_longest_question"]
JEV_LATENCY_RANGE_MS = tuple(_J["latency_ms_range"])  # TypeSafe's stated range; measure your own
PRICES_CHECKED = PRICES["checked"]

# LLM presets: (USD/M input, USD/M output, typical latency in ms for a short
# classification prompt at the lowest reasoning setting). Tiers: "cheap" is the
# cost rival on short bounded decisions; "frontier" shows the accuracy ceiling's
# price; "superseded" models are kept because published measurements used them.
LLM_PRESETS = {k: (v["in"], v["out"], v["latency_ms"]) for k, v in PRICES["llm_presets"].items()}

# Defaults, and why:
# - 40 tokens per question: a Jev request bills the state once plus ~30-50 tokens
#   per question with one-line criteria (alternatives reference, section 2).
# - 60 LLM output tokens: a JSON object with one label is 12-30 tokens with
#   reasoning off (measured on GPT-6 Luna, 2026-10-01); 60 leaves room for a
#   confidence field or a few reasoning tokens. Pass your measured value.
# - 1,500 ms LLM latency when no preset matches: the middle of the 0.4-2.9 s
#   range measured for cheap-tier models at their lowest reasoning setting.
# - Peak multiplier 3: an assumption that business-hours traffic puts about 3x
#   the daily average rate into the peak hour. Replace it with your own peak.
DEFAULT_TOKENS_PER_QUESTION = 40
DEFAULT_LLM_OUTPUT_TOKENS = 60
DEFAULT_LLM_LATENCY_MS = 1500.0
DEFAULT_PEAK_MULTIPLIER = 3.0


def fmt_usd(x: float) -> str:
    if x >= 100:
        return f"${x:,.0f}"
    if x >= 1:
        return f"${x:,.2f}"
    if x >= 0.01:
        return f"${x:.4f}"
    return f"${x:.6f}"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--items-per-day", type=float, required=True, help="number of states (documents, tickets, rows) evaluated per day")
    p.add_argument("--state-tokens", type=float, required=True, help="average tokens of state per request")
    p.add_argument("--questions", type=int, default=1, help="questions per request (default 1)")
    p.add_argument("--tokens-per-question", type=float, default=DEFAULT_TOKENS_PER_QUESTION, help=f"average tokens per question incl. criteria (default {DEFAULT_TOKENS_PER_QUESTION})")
    p.add_argument("--requests-per-item", type=float, default=1.0, help="Jev requests per item, e.g. 2 for a two-stage cascade (default 1)")
    p.add_argument("--jev-price", type=float, default=JEV_PRICE_PER_MTOK, help=f"USD per Mtok input (default {JEV_PRICE_PER_MTOK})")
    p.add_argument("--peak-multiplier", type=float, default=DEFAULT_PEAK_MULTIPLIER, help=f"peak-hour rate = average rate x this (default {DEFAULT_PEAK_MULTIPLIER:g}, an assumption; use your own)")
    p.add_argument("--llm-name", default=None, help="label for the LLM comparison, or a preset key: " + ", ".join(LLM_PRESETS))
    p.add_argument("--llm-input-tokens", type=float, default=None, help="LLM input tokens per item (prompt + content)")
    p.add_argument("--llm-output-tokens", type=float, default=DEFAULT_LLM_OUTPUT_TOKENS, help=f"LLM output tokens per item (default {DEFAULT_LLM_OUTPUT_TOKENS} for a JSON label)")
    p.add_argument("--llm-input-price", type=float, default=None, help="USD per Mtok input for the LLM")
    p.add_argument("--llm-output-price", type=float, default=None, help="USD per Mtok output for the LLM")
    p.add_argument("--llm-latency-ms", type=float, default=None, help=f"assumed LLM latency per item in ms (default: preset value, else {DEFAULT_LLM_LATENCY_MS:g})")
    p.add_argument("--json", action="store_true", help="print machine-readable JSON instead of a report")
    p.add_argument("--list-presets", action="store_true", help="print the built-in LLM price presets and exit")
    if argv is None:
        argv = sys.argv[1:]
    if "--list-presets" in argv:
        print(f"LLM presets from {os.path.basename(PRICES_PATH)} (checked {PRICES_CHECKED}); $/M tokens")
        for tier in ("cheap", "frontier", "superseded"):
            print(f"\n{tier} tier" + (" (kept because published measurements used them)" if tier == "superseded" else ""))
            print("preset                  $/M in   $/M out   latency ms   latency source")
            for k, v in PRICES["llm_presets"].items():
                if v["tier"] == tier:
                    extra = f"  -> {v['superseded_by']}" if v.get("superseded_by") else ""
                    print(f"{k:<22}  {v['in']:>6.3f}   {v['out']:>7.2f}   {v['latency_ms']:>8}   {v['latency_source']}{extra}")
        return 0
    a = p.parse_args(argv)

    q_tokens = a.questions * a.tokens_per_question
    tokens_per_request = a.state_tokens + q_tokens
    requests_per_day = a.items_per_day * a.requests_per_item
    tokens_per_day = requests_per_day * tokens_per_request
    cost_per_day = tokens_per_day / 1e6 * a.jev_price
    cost_per_item = cost_per_day / a.items_per_day if a.items_per_day else 0.0

    avg_rps = requests_per_day / 86_400
    peak_rps = avg_rps * a.peak_multiplier
    peak_tps = peak_rps * tokens_per_request
    peak_rpm = peak_rps * 60

    warnings = []
    if tokens_per_request > JEV_CONTEXT_TOTAL:
        warnings.append(f"request is {tokens_per_request:,.0f} tokens; over the {JEV_CONTEXT_TOTAL:,} total budget. Split the state or the questions.")
    if a.state_tokens + a.tokens_per_question > JEV_CONTEXT_STATE_PLUS_LONGEST_Q:
        warnings.append(f"state + longest question is over {JEV_CONTEXT_STATE_PLUS_LONGEST_Q:,} tokens. Chunk or filter the state in code.")
    if a.state_tokens > 8_000:
        warnings.append("state over ~8k tokens: TypeSafe warns accuracy falls with irrelevant detail (context rot). Filter first.")
    if peak_rps > JEV_RATE_REQUESTS_PER_S:
        warnings.append(f"peak ~{peak_rps:,.1f} req/s exceeds the published {JEV_RATE_REQUESTS_PER_S:,} req/s limit; batch more questions per request, queue, or ask for a higher limit.")
    if peak_tps > JEV_RATE_TOKENS_PER_S:
        warnings.append(f"peak ~{peak_tps:,.0f} tokens/s exceeds the published {JEV_RATE_TOKENS_PER_S:,} tokens/s limit.")

    result = {
        "jev": {
            "tokens_per_request": tokens_per_request,
            "requests_per_day": requests_per_day,
            "tokens_per_day": tokens_per_day,
            "cost_per_item_usd": cost_per_item,
            "cost_per_day_usd": cost_per_day,
            "cost_per_month_usd": cost_per_day * 30,
            "avg_requests_per_s": avg_rps,
            "peak_requests_per_min": peak_rpm,
            "peak_tokens_per_s": peak_tps,
            "latency_ms_range_per_request": list(JEV_LATENCY_RANGE_MS),
            "serial_latency_ms_range_per_item": [x * a.requests_per_item for x in JEV_LATENCY_RANGE_MS],
        },
        "warnings": warnings,
    }

    llm = None
    if a.llm_input_tokens is not None:
        name = a.llm_name or "LLM"
        in_price, out_price = a.llm_input_price, a.llm_output_price
        llm_latency = a.llm_latency_ms
        if a.llm_name in LLM_PRESETS:
            in_price = in_price if in_price is not None else LLM_PRESETS[a.llm_name][0]
            out_price = out_price if out_price is not None else LLM_PRESETS[a.llm_name][1]
            if llm_latency is None:
                llm_latency = LLM_PRESETS[a.llm_name][2]
        if llm_latency is None:
            llm_latency = DEFAULT_LLM_LATENCY_MS
        if in_price is None or out_price is None:
            p.error("--llm-input-price and --llm-output-price are required unless --llm-name is a preset")
        llm_cost_item = (a.llm_input_tokens * in_price + a.llm_output_tokens * out_price) / 1e6
        llm_cost_day = llm_cost_item * a.items_per_day
        llm = {
            "name": name,
            "cost_per_item_usd": llm_cost_item,
            "cost_per_day_usd": llm_cost_day,
            "cost_per_month_usd": llm_cost_day * 30,
            "latency_ms_per_item": llm_latency,
            "cost_ratio_llm_over_jev": (llm_cost_item / cost_per_item) if cost_per_item else None,
        }
        result["llm"] = llm

    if a.json:
        print(json.dumps(result, indent=2))
        return 0

    j = result["jev"]
    print("Jev workload estimate")
    print(f"  tokens per request      {tokens_per_request:>12,.0f}  (state {a.state_tokens:,.0f} + {a.questions} q x {a.tokens_per_question:,.0f})")
    print(f"  requests per day        {requests_per_day:>12,.0f}")
    print(f"  tokens per day          {tokens_per_day:>12,.0f}")
    print(f"  cost per item           {fmt_usd(cost_per_item):>12}")
    print(f"  cost per day            {fmt_usd(cost_per_day):>12}")
    print(f"  cost per month (30d)    {fmt_usd(cost_per_day * 30):>12}")
    print(f"  avg / peak req per s    {avg_rps:>7.2f} / {peak_rps:.2f}   (peak x{a.peak_multiplier:g}; limit {JEV_RATE_REQUESTS_PER_S:,})")
    print(f"  peak tokens per s       {peak_tps:>12,.0f}  (limit {JEV_RATE_TOKENS_PER_S:,})")
    print(f"  peak requests per min   {peak_rpm:>12,.0f}  (limit {JEV_RATE_REQUESTS_PER_MIN:,})")
    lo, hi = j["serial_latency_ms_range_per_item"]
    print(f"  latency per item        {lo:>6.0f}-{hi:.0f} ms  (TypeSafe's stated range x {a.requests_per_item:g} serial requests; measure it)")
    if llm:
        print()
        print(f"{llm['name']} comparison (same items, {a.llm_input_tokens:,.0f} in / {a.llm_output_tokens:,.0f} out tokens each)")
        print(f"  cost per item           {fmt_usd(llm['cost_per_item_usd']):>12}")
        print(f"  cost per day            {fmt_usd(llm['cost_per_day_usd']):>12}")
        print(f"  cost per month (30d)    {fmt_usd(llm['cost_per_month_usd']):>12}")
        print(f"  LLM / Jev cost ratio    {llm['cost_ratio_llm_over_jev']:>12.1f}x")
        lat_note = "preset; source in --list-presets" if (a.llm_name in LLM_PRESETS and a.llm_latency_ms is None) else ("given" if a.llm_latency_ms is not None else "assumed default")
        print(f"  latency per item        {llm_latency:>9,.0f} ms  ({lat_note})")
    if warnings:
        print()
        print("Warnings")
        for w in warnings:
            print(f"  - {w}")
    print()
    print(f"Prices and limits from prices.json, checked {PRICES_CHECKED}; re-check {_J['source']} before quoting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
