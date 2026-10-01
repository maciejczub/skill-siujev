# Eval results

Runs of `evals.json` against the skill on 2026-10-01 and 2026-10-02, following Anthropic's skill-authoring guide:
three models, a no-skill baseline, iteration on observed failures, and a skill-selection check.

## Contents
- Method
- Scores (final version and first round)
- Skill selection (should and should-not trigger)
- What the runs changed in the skill
- Caveats
- How to re-run

## Method

- **Models with the skill:** Claude Haiku 4.5, Claude Sonnet 5.5, Claude Opus 5.5. Each ran as a fresh agent that
  loads the skill the way a skill loads: `SKILL.md` first, then only the files it points to.
- **Rules for every run:** no network, no paid API calls, and the scripts run offline (`estimate_cost.py`,
  `check_report.py`, `probe.py --validate`). The agent never saw `evals.json`.
- **Baseline:** Claude Sonnet 5.5 without the skill, with web search and fetch allowed. Jev was released after its
  training data, so without the web it would know nothing about it.
- **Grading:** a separate Claude Opus 5.5 agent per eval, strict and literal. It marked every expectation PASS or FAIL
  with one line of evidence, and noted factual errors and word counts.
- **Repetitions:** one run per model per eval per round, so a single expectation can flip on rerun.
- **Rounds:**
  - Round 1 used commit a4d1705.
  - Round 2 used afa84f9, after fixing what round 1 exposed.
  - Round 3 re-ran eval 2 on Haiku and Sonnet only, at 15551af, after one more fix.

## Scores

Expectations passed. "Final" is the latest version of the skill each run saw:
- eval 2 is round 3 for Haiku and Sonnet, round 2 for Opus;
- evals 1, 3 and 4 are round 2;
- eval 5 is round 1, which every model passed in full with the skill.

| Eval (expectations) | Haiku 4.5 | Sonnet 5.5 | Opus 5.5 | Baseline: Sonnet 5.5, no skill, web on |
|---|---|---|---|---|
| 1. Scan a helpdesk repo (17) | 8 | 16 | 16 | 9 |
| 2. Polish listing moderation, single decision (13) | 9 | 13 | 13 | 12 |
| 3. Quick cost question vs DeepSeek (9) | 7 | 8 | 8 | 5 |
| 4. Greenfield product opportunities (11) | 7 | 10 | 10 | 8 |
| 5. "Can Jev be my coding agent's model?" (7) | 7 | 7 | 7 | 4 |
| **Final total (57)** | **38 (67 %)** | **54 (95 %)** | **54 (95 %)** | **38 (67 %)** |
| Round 1 total (57) | 32 (56 %) | 51 (89 %) | 50 (88 %) | 38 (67 %) |

What the scores say:

- **Sonnet and Opus with the skill** pass nearly everything. Their remaining misses are judgment calls, such as one
  shared threshold for two moderation categories, or naming where to re-check a price.
- **The no-skill baseline** gets the broad picture right from the web. What it misses:
  - rival pricing in the cheap tier
  - a graded verdict scale
  - new capabilities
  - dated facts
  - the answer to the coding-agent question

  It also cited misattributed benchmark figures in two runs.
- **Haiku with the skill** handles quick questions well: eval 5 7/7, eval 3 7/9. In whole-repository scans it misses
  candidates, packs items to rank into one state, and makes arithmetic slips (eval 1 8/17 in both rounds). Use
  Sonnet or Opus for scans and reports someone will build on; Haiku is fine for quick answers.

## Skill selection

All three models got the same task: from the installed skills' names and descriptions only (this skill's
914-character description plus eight real skills from the same environment), pick the skill for 14 requests:

- 7 requests where this skill should be chosen: Jev and TypeSafe questions, "is an LLM overkill for routing", Liquid
  D1 vs Jev, the coding-agent question, and opportunities for a calibrated classifier;
- 7 where it should not: a summary of tickets, a regex, a Claude API retry, a chart, a code review, Polish TTS, and a
  translation.

| Model | Chosen when it should be | Chosen when it should not be |
|---|---|---|
| Haiku 4.5 | 7/7 | 0/7 |
| Sonnet 5.5 | 7/7 | 0/7 |
| Opus 5.5 | 7/7 | 0/7 |

## What the runs changed in the skill

Each change came from a failure seen in a transcript, not from a guess:

| Observed in a run | Change |
|---|---|
| `check_report.py --kind quick` demanded the full report format, contradicting "do not pad a quick answer" (found by Sonnet and Opus) | quick mode checks only length, duplicates and cost provenance; a fixture covers it |
| Quick cost answers skipped option tokens, the rival's dated price, rate limits, latency, an `other` option, or the incumbent's caching | a one-line-each must-include list under "A quick question" (eval 3: Haiku 3 → 7, Opus 6 → 8) |
| Greenfield answers read as audits, skipped families, gave no total or no reason for the pilot order | the greenfield route walks every family, totals the lines, explains the first pilot (eval 4: Opus 8 → 10, Sonnet 9 → 10) |
| Scan reports of 3,400–4,400 words with pilot specs pasted in | specs live next to the report; the word ceiling counts code blocks (eval 1 reports now 2,350–2,460 words) |
| Only monthly costs; hand-computed ratios wrong | per item, per day and per month copied from the script, ratios included |
| Rules engines dropped, auto-actions inside the uncertain band | two design rules in the fit checklist: keep the floor; never auto-act inside the band |
| PILOT FIRST verdicts without the vendor's language statement, with synthetic data called real, without numeric pass bars | a must-include list for PILOT FIRST (eval 2: Haiku 7 → 9, Sonnet 12 → 13) |
| Eval 4's matching expectation penalised user-written rules asked as separate questions, which the skill recommends | the expectation was clarified; record-to-record matching still requires one pair per request |

## Caveats

- **One run per cell.** Differences of one or two expectations are within run-to-run noise.
- **The grader is a Claude model** grading Claude models. Expectations are literal and evidence is quoted, but no
  human graded these runs.
- **The baseline differs in two ways:** no skill and web access. It measures "a capable agent without this skill",
  not "the same agent minus one file".
- **The skill-selection test is a proxy:** one model sees a list of descriptions, not a live session with dozens of
  installed skills.

## How to re-run

1. For each eval in `evals.json`, give a fresh agent the `prompt` with the skill installed (and the files in `files`).
   Write the answer to a file.
2. Run the same prompt once without the skill, as the baseline.
3. Grade each answer against `expectations`, strictly, PASS or FAIL with evidence.
4. For the selection check, add `should_trigger: false` cases and real neighbouring skills, then compare the chosen
   skill with `should_trigger`.

`tools/check_skill.py` (also run in CI) covers the mechanical checks: frontmatter, line budget, contents sections,
reference depth, `prices.json` against the tables, and script smoke tests.
