#!/usr/bin/env python3
"""Check a "Should I use Jev?" report against itself before it is handed over.

Standard library only. The report must follow assets/verdict-template.md:
"## Summary" with the verdict counts written as numbers ("2 USE, 1 PILOT FIRST,
3 NO"), "## Candidates" with a table that has a Verdict column,
"## Candidate N: <name>" sections and, for new capabilities,
"### Proposal X: <name>" sections, each with one "**Verdict: <VERDICT>.**" line.

Checks (each failure prints the exact problem):
  - every candidate and proposal section has exactly one valid verdict
  - every table row has a "## Candidate N" section, with the same verdict
  - the summary states verdict counts, and they equal the counts in the sections
  - no bullet line appears twice (a duplicated list)
  - dollar figures appear only if the report cites an estimate_cost.py run
  - the word count stays under the ceiling for --kind (quick 500, single 1,200, scan 2,500)

Usage:
  python3 check_report.py report.md --kind scan
Exit code 0 when every check passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

VERDICTS = ("USE WITH GUARDS", "PILOT FIRST", "USE", "NO")  # longest first, so "USE" never eats "USE WITH GUARDS"
VERDICT_RE = "|".join(re.escape(v) for v in VERDICTS)
# Word ceilings from SKILL.md, Step 4.
CEILINGS = {"quick": 500, "single": 1200, "scan": 2500}


def sections(text: str, level: int) -> list[tuple[str, str]]:
    """Split on headings of exactly `level` #'s; return (heading, body) pairs."""
    pat = re.compile(rf"^{'#' * level} (?!#)(.+)$", re.M)
    hits = list(pat.finditer(text))
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        out.append((m.group(1).strip(), text[m.end():end]))
    return out


def section_body(text: str, title: str) -> str | None:
    for h, body in sections(text, 2):
        if h.lower().startswith(title.lower()):
            return body
    return None


def verdicts_in(body: str) -> list[str]:
    return [m.group(1) for m in re.finditer(rf"\*\*Verdict[:.]?\**\s*\**\s*({VERDICT_RE})\b", body)]


def table_rows(body: str) -> list[tuple[str, str]]:
    """(row id, verdict) from the first markdown table that has a Verdict column."""
    lines = [l.strip() for l in body.splitlines() if l.strip().startswith("|")]
    if not lines:
        return []
    head = [c.strip().lower() for c in lines[0].strip("|").split("|")]
    if "verdict" not in head:
        return []
    vi = head.index("verdict")
    rows = []
    for l in lines[1:]:
        cells = [c.strip() for c in l.strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue  # separator row
        if len(cells) > vi:
            rows.append((cells[0], re.sub(r"[*`]", "", cells[vi]).strip().upper()))
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("report")
    p.add_argument("--kind", choices=sorted(CEILINGS), default="scan", help="report kind, sets the word ceiling (default scan)")
    a = p.parse_args(argv)
    try:
        text = open(a.report, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {a.report}: {e}")
        return 2
    errors = []

    # 1. sections and their verdicts
    cand = {}
    for h, body in sections(text, 2):
        m = re.match(r"Candidate\s+(\d+)\s*:", h, re.I)
        if m:
            v = verdicts_in(body)
            if len(v) != 1:
                errors.append(f'"## {h}": expected exactly one "**Verdict: ...**" line, found {len(v)}')
            cand[m.group(1)] = v[0] if v else None
    props = {}
    for h, body in sections(text, 3):
        if re.match(r"Proposal\b", h, re.I):
            v = verdicts_in(body)
            if len(v) != 1:
                errors.append(f'"### {h}": expected exactly one "**Verdict: ...**" line, found {len(v)}')
            props[h] = v[0] if v else None
    if not cand and not props:
        errors.append('no "## Candidate N:" or "### Proposal X:" sections found; follow assets/verdict-template.md')

    # 2. table rows vs sections
    cbody = section_body(text, "Candidates")
    rows = table_rows(cbody) if cbody else []
    if cand and not rows:
        errors.append('"## Candidates" table with a Verdict column not found')
    for rid, rv in rows:
        num = re.sub(r"\D", "", rid)
        if num not in cand:
            errors.append(f'table row {rid}: no "## Candidate {num}:" section')
        elif cand[num] and rv != cand[num]:
            errors.append(f"candidate {num}: table says {rv}, section says {cand[num]}")
    for num in cand:
        if rows and num not in {re.sub(r'\D', '', r) for r, _ in rows}:
            errors.append(f'"## Candidate {num}" is missing from the candidate table')

    # 3. summary counts
    summary = section_body(text, "Summary") or ""
    stated = Counter()
    for m in re.finditer(rf"\b(\d+)\s+({VERDICT_RE})\b", summary):
        stated[m.group(2)] += int(m.group(1))
    actual = Counter(v for v in list(cand.values()) + list(props.values()) if v)
    if not stated:
        errors.append('summary states no verdict counts; write them as numbers, e.g. "2 USE, 1 PILOT FIRST, 3 NO"')
    elif stated != actual:
        fmt = lambda c: ", ".join(f"{c[v]} {v}" for v in VERDICTS if c[v]) or "none"
        errors.append(f"summary counts ({fmt(stated)}) differ from the sections ({fmt(actual)}; candidates and proposals together)")

    # 4. duplicated lists
    bullets = [l.strip() for l in text.splitlines() if re.match(r"\s*[-*] \S", l) and len(l.strip()) > 25]
    for line, n in Counter(bullets).items():
        if n > 1:
            errors.append(f"bullet repeated {n} times: {line[:80]}")

    # 5. cost figures must trace to a script run
    if re.search(r"\$\s?\d", text) and "estimate_cost" not in text:
        errors.append("dollar figures without a cited estimate_cost.py run; name the run (command or 'from estimate_cost.py') in Economics or Assumptions")

    # 6. length
    body_no_code = re.sub(r"```.*?```", "", text, flags=re.S)
    words = len(re.findall(r"\S+", body_no_code))
    if words > CEILINGS[a.kind]:
        errors.append(f"{words:,} words; the ceiling for a {a.kind} report is {CEILINGS[a.kind]:,}. Cut restatements and extra citations first")

    if errors:
        print(f"{len(errors)} problem(s) in {a.report}:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {len(cand)} candidates, {len(props)} proposals, {words:,} words ({a.kind} ceiling {CEILINGS[a.kind]:,})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
