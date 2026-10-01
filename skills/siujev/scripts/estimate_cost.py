#!/usr/bin/env python3
"""Estimate the cost and latency of a Jev (TypeSafe System One) workload and
compare it with doing the same judgment through an LLM.

Standard library only. Prices are defaults you can override; they were checked
on 2026-09-21 and re-checked on 2026-10-01 (Jev: https://docs.typesafe.ai/models.md;
LLM presets: vendor pricing pages and OpenRouter). Re-check before quoting them
to anyone. Run with --list-presets to see the built-in LLM price presets.

Examples
--------
  # 50k support tickets/day, ~600 tokens of state, 6 questions of ~40 tokens each
  python3 estimate_cost.py --items-per-day 50000 --state-tokens 600 \
      --questions 6 --tokens-per-question 40

  # Same, comparing against a same-tier LLM prompt of 900 input / 60 output tokens
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
import sys

JEV_PRICE_PER_MTOK = 0.042  # USD per million input tokens; output is free
# Published per-account limits on 2026-10-01 (were 250k tokens/s and 1,200 req/min
# at launch); TypeSafe says they adjust dynamically.
JEV_RATE_TOKENS_PER_S = 100_000
JEV_RATE_REQUESTS_PER_S = 40
JEV_RATE_REQUESTS_PER_MIN = JEV_RATE_REQUESTS_PER_S * 60
JEV_CONTEXT_TOTAL = 64_000
JEV_CONTEXT_STATE_PLUS_LONGEST_Q = 32_000
JEV_LATENCY_RANGE_MS = (100, 500)  # TypeSafe's stated range; measure your own

# Reference LLM prices (USD per million tokens, input / output) and a typical
# latency in ms for a short classification prompt. Checked 2026-09-21/22 and
# re-checked 2026-10-01 on vendor pages and OpenRouter; these move monthly. For
# cost, compare against the flash tier (Jev's accuracy band on short bounded
# decisions). For the accuracy ceiling, or when the incumbent is a frontier
# model, use the frontier presets. Latency for reasoning-default models assumes
# reasoning set to its lowest level. Models released after 2026-09-21 have no
# latency measurement yet: their value is the predecessor's, marked "assumed";
# pass --llm-latency-ms with your own measurement.
LLM_PRESETS = {
    # cheap / flash tier (Jev's accuracy band)
    "qwen3.7-flash": (0.03, 0.13, 750),
    "qwen3.8-flash": (0.15, 0.47, 700),
    "glm-5.3-flash": (0.15, 0.50, 900),
    "deepseek-v4.1-flash": (0.15, 0.60, 1700),   # off-peak; peak is 0.30 / 1.20
    "gemini-2.5-flash-lite": (0.10, 0.40, 400),
    "gemini-3.5-flash-lite": (0.30, 2.50, 1200),
    "gpt-5-nano": (0.05, 0.40, 1300),
    "gpt-5.6-luna": (0.20, 1.20, 1000),
    "gpt-6-luna": (0.10, 0.50, 1000),            # released 2026-09-22; latency assumed
    "ministral-8b": (0.15, 0.15, 350),
    "mistral-small-4": (0.15, 0.60, 420),
    "nova-micro": (0.035, 0.14, 380),
    "claude-haiku-4-5": (1.00, 5.00, 800),
    # frontier tier: use to show the accuracy ceiling's price, or when the
    # incumbent is one of these
    "gpt-5.6-terra": (2.00, 12.00, 1500),
    "gpt-5.6-sol": (4.00, 20.00, 3000),          # promo price, at least to 2026-11-21
    "gpt-6-sol": (2.00, 10.00, 3000),            # released 2026-09-22; latency assumed
    "gpt-6.1-sol": (2.00, 10.00, 3000),          # released 2026-09-29; latency assumed
    "gpt-6-astra": (10.00, 50.00, 4000),
    "claude-sonnet-5-5": (2.00, 10.00, 2200),    # released 2026-09-28; latency assumed
    "claude-sonnet-5": (2.00, 10.00, 2200),
    "claude-opus-5-5": (4.00, 20.00, 3300),      # released 2026-09-22; latency assumed
    "claude-opus-5": (5.00, 25.00, 3300),
    "claude-fable-5-1": (10.00, 50.00, 5000),
    "gemini-3.8-flash": (0.75, 3.75, 1800),
    "grok-4.7": (2.00, 6.00, 4300),              # released 2026-09-21; latency assumed
    "grok-4.6": (2.00, 6.00, 4300),
    "kimi-k3": (3.00, 15.00, 1900),
    "deepseek-v4-pro": (0.66, 1.98, 2400),   # off-peak; peak is 1.32 / 3.96
}


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
    p.add_argument("--tokens-per-question", type=float, default=40, help="average tokens per question incl. criteria (default 40)")
    p.add_argument("--requests-per-item", type=float, default=1.0, help="Jev requests per item, e.g. 2 for a two-stage cascade (default 1)")
    p.add_argument("--jev-price", type=float, default=JEV_PRICE_PER_MTOK, help=f"USD per Mtok input (default {JEV_PRICE_PER_MTOK})")
    p.add_argument("--peak-multiplier", type=float, default=3.0, help="peak-hour rate = average rate x this (default 3)")
    p.add_argument("--llm-name", default=None, help="label for the LLM comparison, or a preset key: " + ", ".join(LLM_PRESETS))
    p.add_argument("--llm-input-tokens", type=float, default=None, help="LLM input tokens per item (prompt + content)")
    p.add_argument("--llm-output-tokens", type=float, default=60, help="LLM output tokens per item (default 60 for a JSON label)")
    p.add_argument("--llm-input-price", type=float, default=None, help="USD per Mtok input for the LLM")
    p.add_argument("--llm-output-price", type=float, default=None, help="USD per Mtok output for the LLM")
    p.add_argument("--llm-latency-ms", type=float, default=None, help="assumed LLM latency per item in ms (default: preset value, else 1500)")
    p.add_argument("--json", action="store_true", help="print machine-readable JSON instead of a report")
    p.add_argument("--list-presets", action="store_true", help="print the built-in LLM price presets and exit")
    if argv is None:
        argv = sys.argv[1:]
    if "--list-presets" in argv:
        print("preset                  $/M in   $/M out   latency ms (prices re-checked 2026-10-01)")
        for k, (i, o, l) in LLM_PRESETS.items():
            print(f"{k:<22}  {i:>6.3f}   {o:>7.2f}   {l:>6}")
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
            llm_latency = 1500.0
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
        print(f"  latency per item        {llm_latency:>9,.0f} ms  (assumed)")
    if warnings:
        print()
        print("Warnings")
        for w in warnings:
            print(f"  - {w}")
    print()
    print("Prices and limits checked 2026-10-01; re-check https://docs.typesafe.ai/models.md before quoting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
