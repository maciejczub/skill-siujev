# Should I use Jev? — <system or feature name>

Date: <YYYY-MM-DD>. Facts checked against docs.typesafe.ai on <date>.

## Summary

<Two or three sentences: how many candidates and proposals were found, the
verdict counts written as numbers over candidates and proposals together
(e.g. "2 USE, 1 USE WITH GUARDS, 1 PILOT FIRST, 3 NO"), and the single most
valuable one.>

## Candidates

| # | Where | Judgment | Shape | Verdict | Why (one line) |
|---|---|---|---|---|---|
| 1 | `path/file.py:42` | assign ticket to team | classification | USE WITH GUARDS | replaces 1.8 s LLM call; non-English 20% of traffic |

## Candidate 1: <name>

**Decision.** <what is judged, over what input, and what the program does with the answer>

**Verdict: USE / USE WITH GUARDS / PILOT FIRST / NO.**

**Why.** <2–4 sentences tying the verdict to the fit checklist: shape, blockers, green and yellow signals>

**Sketch.** <state fields; questions as `id: type — instructions — options/levels`; how code combines answers; thresholds and where uncertain cases go>

**Economics.** <table or two lines from estimate_cost.py: tokens per request, cost per item, per day and per month for Jev vs incumbent and the best rival decision model, latency per item>

**Risks and guards.** <bullets: each yellow signal with its guard>

**Alternative if not Jev.** <the best other option, including a rival decision model, and when it would win>

**Next step.** <pilot: number of items, labels, probe.py flags, and the spec's file name (specs live next to the report, not in it); or "implement with the official TypeSafe skill">

## Candidate 2: ...

## New capabilities worth a pilot

Proposals from the opportunity pass: things the product does not do today
that a sub-second, sub-cent judgment makes practical. Same structure as a
candidate (decision, verdict, sketch, economics, guards, next step), plus one
line on **what the user gets** that they cannot get now.

### Proposal A: <name>

**What the user gets.** <one sentence>

**Decision.** ...

**Verdict: USE / USE WITH GUARDS / PILOT FIRST / NO.**

**Sketch.** ... **Economics.** ... **Guards.** ... **Next step.** ...

## Not candidates (and why)

- <place> — <one line: generation / arithmetic / image / already deterministic>

## Assumptions

- <volumes, token counts, latency of the incumbent, prices used and their check date>
- <the estimate_cost.py commands behind every cost figure>

<!-- Before handing over: python3 scripts/check_report.py report.md --kind scan|single|quick -->
