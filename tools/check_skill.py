#!/usr/bin/env python3
"""Repository checks for the siujev skill (run locally and in CI).

Enforces the rules from Anthropic's skill-authoring best practices that can be
checked mechanically, plus this repo's own consistency rules:
  - SKILL.md frontmatter: name format and reserved words; description present,
    <= 1,024 characters, no XML tags, no prices
  - SKILL.md body under 500 lines; reference paths written as references/<file>
  - every reference over 100 lines has a "## Contents" section
  - no reference file points to another reference file (one level deep)
  - no Windows-style paths
  - scripts/prices.json agrees with the price tables in references/alternatives.md
    and with the Jev price and limits in references/jev-facts.md
  - scripts compile; evals.json is well formed
  - smoke tests: probe.py --validate, check_report.py on good/bad fixtures,
    estimate_cost.py --list-presets
Exit code 0 when everything passes, 1 otherwise. Standard library only.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "siujev"
REFS = SKILL / "references"
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def frontmatter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        err("SKILL.md: missing YAML frontmatter")
        return "", text
    fm, body = m.group(1), m.group(2)
    name = re.search(r"^name:\s*(\S+)\s*$", fm, re.M)
    if not name:
        err("SKILL.md: frontmatter has no name")
    else:
        n = name.group(1)
        if not re.fullmatch(r"[a-z0-9-]{1,64}", n):
            err(f"SKILL.md: name {n!r} must be 1-64 lowercase letters, digits or hyphens")
        if "anthropic" in n or "claude" in n:
            err(f"SKILL.md: name {n!r} contains a reserved word")
    d = re.search(r"^description:\s*>?\s*\n((?:[ \t]+.*\n?)+)", fm, re.M) or re.search(r"^description:\s*(.+)$", fm, re.M)
    desc = " ".join(l.strip() for l in d.group(1).splitlines()).strip() if d else ""
    if not desc:
        err("SKILL.md: description is empty")
    if len(desc) > 1024:
        err(f"SKILL.md: description is {len(desc)} characters; the limit is 1,024")
    if re.search(r"<[^>]+>", desc):
        err("SKILL.md: description contains an XML tag")
    if re.search(r"\$\s?\d", desc):
        err("SKILL.md: description contains a price; prices date quickly and the description is always loaded")
    return desc, body


def skill_body(body: str):
    n = len(body.splitlines())
    if n >= 500:
        err(f"SKILL.md: body has {n} lines; keep it under 500")
    for f in REFS.glob("*.md"):
        for m in re.finditer(rf"(?<![/\w-]){re.escape(f.name)}", body):
            err(f"SKILL.md: write references/{f.name}, not a bare {f.name} (offset {m.start()})")


def references():
    names = [f.name for f in REFS.glob("*.md")]
    for f in sorted(REFS.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if len(text.splitlines()) > 100 and "## Contents" not in text:
            err(f"references/{f.name}: over 100 lines without a '## Contents' section")
        for other in names:
            if other != f.name and re.search(rf"(?<![\w-]){re.escape(other)}", text):
                err(f"references/{f.name}: points to {other}; keep references one level deep (route from SKILL.md)")


def no_backslash_paths():
    for f in list(SKILL.rglob("*.md")) + [ROOT / "README.md"]:
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\b(?:scripts|references|assets|evals)\\\w", line):
                err(f"{f.relative_to(ROOT)}:{i}: Windows-style path")


def numbers(row: str) -> set[float]:
    return {float(x) for x in re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", row.replace(",", ""))}


def find_row(text: str, name: str) -> str | None:
    for line in text.splitlines():
        cell = line.strip().lstrip("|").strip().replace("**", "")
        if line.strip().startswith("|") and cell.startswith(name) and not re.match(r"[\w.]", cell[len(name):len(name) + 1] or " "):
            return line
    return None


def prices():
    try:
        P = json.loads((SKILL / "scripts" / "prices.json").read_text())
    except ValueError as e:
        err(f"scripts/prices.json: invalid JSON: {e}")
        return
    alt = (REFS / "alternatives.md").read_text(encoding="utf-8")
    for key, v in P["llm_presets"].items():
        row = find_row(alt, v["name"])
        if row is None:
            err(f"prices.json preset {key}: no table row starting with {v['name']!r} in references/alternatives.md")
            continue
        got = numbers(row)
        for field in ("in", "out"):
            if float(v[field]) not in got:
                err(f"prices.json preset {key}: {field} price {v[field]} not found in its alternatives.md row")
        if v["tier"] == "superseded" and v.get("superseded_by") not in P["llm_presets"]:
            err(f"prices.json preset {key}: superseded_by {v.get('superseded_by')!r} is not a preset")
    for key, v in P.get("decision_models", {}).items():
        row = find_row(alt, v["name"])
        if row is None:
            err(f"prices.json decision model {key}: no row starting with {v['name']!r} in alternatives.md §2c")
        elif v["in"] > 0 and float(v["in"]) not in numbers(row):
            err(f"prices.json decision model {key}: price {v['in']} not found in its alternatives.md row")
    facts = (REFS / "jev-facts.md").read_text(encoding="utf-8")
    j = P["jev"]
    for needle in (f"${j['price_in']}", f"{j['rate_tokens_per_s']:,} tokens/s", f"{j['rate_requests_per_s']} requests/s"):
        if needle not in facts:
            err(f"references/jev-facts.md does not state {needle!r} from prices.json")


def scripts_compile():
    for f in (SKILL / "scripts").glob("*.py"):
        try:
            compile(f.read_text(encoding="utf-8"), str(f), "exec")  # in memory: no __pycache__
        except SyntaxError as e:
            err(f"{f.relative_to(ROOT)}:{e.lineno}: {e.msg}")


def evals():
    try:
        E = json.loads((ROOT / "evals" / "evals.json").read_text())
    except ValueError as e:
        err(f"evals/evals.json: invalid JSON: {e}")
        return
    ids = [e.get("id") for e in E.get("evals", [])]
    if len(ids) < 3:
        err("evals/evals.json: fewer than three evals")
    if len(set(ids)) != len(ids):
        err("evals/evals.json: duplicate ids")
    for e in E["evals"]:
        if not e.get("prompt") or not e.get("expectations"):
            err(f"eval {e.get('id')}: needs a prompt and at least one expectation")
        if not isinstance(e.get("should_trigger"), bool):
            err(f"eval {e.get('id')}: should_trigger must be true or false")


def smoke():
    s = SKILL / "scripts"
    fx = ROOT / "evals" / "fixtures" / "reports"
    runs = [
        ([sys.executable, str(s / "probe.py"), str(SKILL / "assets" / "pilot-spec-example.json"), "--validate"], 0),
        ([sys.executable, str(s / "check_report.py"), str(fx / "report-ok.md"), "--kind", "single"], 0),
        ([sys.executable, str(s / "check_report.py"), str(fx / "report-bad.md"), "--kind", "single"], 1),
        ([sys.executable, str(s / "check_report.py"), str(fx / "quick-ok.md"), "--kind", "quick"], 0),
        ([sys.executable, str(s / "estimate_cost.py"), "--list-presets"], 0),
        ([sys.executable, str(s / "estimate_cost.py"), "--items-per-day", "1000", "--state-tokens", "500",
          "--llm-name", "gpt-6-luna", "--llm-input-tokens", "800"], 0),
    ]
    for cmd, want in runs:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != want:
            err(f"smoke test {' '.join(Path(c).name for c in cmd[1:3])}: exit {r.returncode}, expected {want}\n{r.stdout[-400:]}{r.stderr[-400:]}")


def main() -> int:
    desc, body = frontmatter()
    skill_body(body)
    references()
    no_backslash_paths()
    prices()
    scripts_compile()
    evals()
    smoke()
    if errors:
        print(f"{len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: description {len(desc)} chars, SKILL.md body {len(body.splitlines())} lines, all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
