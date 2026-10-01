---
name: siujev
description: >
  Decides whether and where to use Jev, TypeSafe AI's System One decision
  model (typed Choice, Score and Noul answers with calibrated probabilities; no
  text generation), and how it compares with rival decision models such as
  Liquid D1. Use when someone asks whether Jev or TypeSafe fits a feature;
  wants to find where a classifier could replace keyword heuristics, regex
  standing in for meaning, review queues, or LLM calls that only return a
  label, score, or yes/no; compares Jev with plain code, embeddings,
  rerankers, a fine-tuned classifier, another decision model, or a cheap LLM
  on accuracy, latency, cost, and rate limits; or asks what a fast, cheap
  judgment would make possible in a codebase, design, or product idea. Also
  covers "can Jev power my coding agent" and "is an LLM overkill for this
  classification". Not for implementing the integration (hand off to
  TypeSafe's own skill) or for generative tasks.
license: MIT
---

# Should I use Jev?

Jev returns typed judgments, not text. That single fact decides most cases:
if the program needs a label, a score on a rubric, a yes/no probability, a
ranking, or a "which of these", Jev may fit; if it needs prose, code, a summary,
a number computed from other numbers, or a chain of reasoning, it does not.
Your job is twofold: find the decisions that already have the first shape and
check whether Jev does them better, and find the judgments the product does
not make today because a judgment used to cost seconds and cents. The second
is where Jev has been paying off in ways earlier classifiers did not: inside
loops, queries, keystroke handlers, agent steps, and rules users write in
plain language. Then check each candidate honestly against what Jev can do
today, what it costs, and what else would do the job.

Read `references/jev-facts.md` first if you have not used Jev before in this
session. It is short and dated; it lists primitives, limits, prices, rate
limits, and the nine documented failure modes. Hold two calibration points in
mind throughout. First, accuracy: on short, bounded decisions Jev ties
mid-frontier models and the cheap tier; on many-way overlapping labels and on
long, fuzzy, multi-field documents it trails the frontier, and a
confidence-gated cascade recovers most of that gap at a fraction of the
frontier's cost (figures and sources in `references/evidence.md` §1).
Second, its typed output guarantees the *shape* of an answer, never its
correctness. Paths in this file are relative to the skill directory.

## Decide which job you are doing

- **One decision point** ("should I use Jev for X?"): skip the scan, go straight
  to the fit check for X, then economics, then the verdict.
- **A whole system, repo, or design** ("where could Jev fit?"): scan first,
  in two passes (replace what exists; propose what becomes possible), write a
  shortlist, fit-check the five or six most valuable items, and say which
  others were left for a later pass.
- **A greenfield or product question** ("we're building X, what could Jev
  add?"): opportunity pass only, from `references/use-case-catalog.md`, then
  fit-check the best two or three proposals.
- **A comparison** ("Jev vs GPT/DeepSeek/embeddings/Liquid D1 for X"): fit
  check, then `references/alternatives.md`, then economics with the specific
  rival.
- **A quick question** ("is it really 400x cheaper for us?"): answer it
  directly with the numbers, the source of each number, and the one or two
  caveats that change the decision. The full report format is for scans and
  for decisions someone will build on; do not pad a quick answer into one.
- **"Can Jev be the model behind my coding agent or chatbot?"** No, and say
  so in a few lines. Jev generates no text, calls no tools and edits no
  files, and TypeSafe's own coding-agents page says there is no setting that
  makes a coding agent Jev-powered. Then give TypeSafe's redirects from
  "Jev and coding agents" in `references/jev-facts.md`: TypeSafe's skill to
  write code that *uses* Jev, the Quick start and Patterns to build with it,
  and the Playground to try it. If the real question is which LLM each
  request should go to, that is a routing decision: treat it as one decision
  point, with Jev Router (an LLM router that uses Jev) or a self-built Choice
  over models as the candidates.

Do not start by praising or dismissing Jev. Start by writing down the decision
in one line: *what is judged, over what input, and what the code does with the
answer*. Most bad verdicts come from never stating this.

For a scan, a greenfield shortlist, or any report someone will build on, copy
this checklist into your working notes and tick it off:

```
Jev assessment progress:
- [ ] 0. Each decision written in one line (what is judged, over what input, what code does with it)
- [ ] 1. Scan: replacement pass, then opportunity pass; candidate table (scans only)
- [ ] 2. Fit check per candidate: blockers, shape, signals, failure modes
- [ ] 3. scripts/estimate_cost.py run per candidate and per rival; raw output kept
- [ ] 4. Verdicts written from assets/verdict-template.md, within the word ceiling
- [ ] 5. A pilot spec for every PILOT FIRST, checked with scripts/probe.py --validate
- [ ] 6. scripts/check_report.py passes on the report
```

## Step 1: Scan (only for whole systems)

Follow `references/scan-signals.md`. You are looking for judgments about
unstructured text that the program then branches, sorts, filters, or routes on.
Three families: judgments written as brittle code, judgments delegated to an
LLM whose output is a label, and judgments made by people who could see only
the uncertain cases. Use grep on the patterns listed there, read the prompt
files, and look at review queues and issue trackers. Ignore deterministic
parsing that works, prose generation, arithmetic, and image or audio inputs
without a text step.

That is the **replacement pass**. Then do the **opportunity pass**: walk the
same reference's family table (semantic conditions in code, judge-everything
columns, real-time loops, agent and harness decisions, verifying other AI,
generate-then-judge, search without an index, matching, queue triage, ML
features, control loops, plain-language personalisation) and ask, for each
loop, table, stream, queue, and user setting in the product, whether a
sub-second, sub-cent, calibrated judgment would enable something the product
does not do today. `references/use-case-catalog.md` has named examples with
numbers for each family; read it during this pass to make proposals concrete
rather than generic. This pass is where Jev has surprised people, and the one
an agent skips unless told to do it. Propose two to four new capabilities that
fit the domain, sketched like any other candidate.

Output of this step: a table, one line per candidate, in the form given in
`references/scan-signals.md` (where, what is judged, shape, current
implementation or "new capability", volume and latency context). Keep it to
what you can support with a file and line, a requirement sentence, or a stated
product goal.

## Step 2: Fit check (per candidate)

Work through `references/fit-checklist.md` in order:

1. **Hard blockers.** Generation (including "be the model behind an agent"),
   non-enumerable answers with no candidate generator, arithmetic or date
   logic at the core, multi-hop reasoning, non-text input, state over 32k
   tokens that cannot be filtered, on-prem requirement, or an existing trained
   classifier that already meets the bar. Any one of these is a NO for the
   decision as stated. Often the decision can be restated so a *part* of it
   fits (Jev selects among regex candidates; code does the arithmetic; an LLM
   generates and Jev verifies). Say so explicitly rather than forcing the
   whole thing in or throwing the whole thing out.
2. **Decision shape.** Map to one of the shapes in the table (classification,
   detection, scoring, routing, ranking, search, verification, extraction by
   selection, matching, feature extraction, pre-filter). Note the primitive and
   the TypeSafe pattern or cookbook that matches. If nothing fits, it is not a
   Jev job.
3. **Green and yellow signals.** Green signals strengthen USE. Each yellow
   signal (non-English, adversarial input, long noisy state, overlapping
   options, world knowledge, irreversible automatic actions, rate-limit
   pressure, need for explanations, vendor risk) needs a named guard in the
   verdict, not a shrug. When the input language is not English, say in the
   verdict what the vendor states (English is the primary training language;
   other languages are accepted with lower accuracy) and whether any
   measurement exists for that language. `references/evidence.md` §5b and §5d
   hold the only Polish measurements known (two small synthetic sets, checked
   2026-10-01); for other Slavic languages there are none.

Cross-check the sketch against the failure-mode table in
`references/jev-facts.md`. The common traps: asking Jev to count or compare
numbers, feeding it dates, hiding three judgments in one question, sending the
whole document when one field matters, and trusting it as the sole gate
against hostile input. TypeSafe's own advice is that when you find yourself
explaining what you *meant* by a question, that explanation is the missing
half of the instruction.

## Step 3: Economics

Numbers separate "would work" from "worth doing". Get token counts by
measuring a few real inputs (about 4 characters per token for English; JSON
structure adds 10–30 %). Then run:

```bash
python3 scripts/estimate_cost.py --items-per-day N --state-tokens S --questions Q \
    [--llm-name <preset or label> --llm-input-tokens I --llm-output-tokens O]
```

It prints cost per item, day, and month, peak request and token rates against
the published limits, and a latency range, and warns when the state exceeds the
context budget or the load exceeds the rate limits. Prices and limits come
from `scripts/prices.json`, the single dated source for every number the
script uses; `--list-presets` prints them by tier. Use the tiers for different
questions:

- **Cost.** The honest rival is the cheap tier
  (`references/alternatives.md` §2). Per-decision arithmetic there shows why
  the vendor's headline multiple does not survive contact with a same-tier
  rival.
- **Accuracy ceiling.** Name where Jev stands against the frontier tier for
  this task type (`references/evidence.md` §1, `references/alternatives.md`
  §2b). When the incumbent is a frontier model or the bar is frontier
  accuracy, price the cascade arm too: Jev behind a high confidence gate, with
  the frontier model handling the rest.
- **Direct rivals.** Other decision models take Jev's exact request body
  (`references/alternatives.md` §2c, measurements in
  `references/evidence.md` §5d). Name the best of them in the verdict and
  pilot it as a second arm.
- **No model at all.** Always also compare against plain code or an existing
  trained classifier whenever one could do the job.

Copy cost and rate figures from the script's output into the report rather
than re-deriving them by hand; hand arithmetic on per-day versus per-month
figures is where reports have slipped. Run the script once per candidate and
once per rival, and keep the raw output next to the report.

Then answer three questions in the verdict: does the per-item saving pay for
integration and a pilot; does the latency change the product or only a batch
job's runtime; and will anyone act on the probabilities (review queue,
thresholds, fallback). If the answers are no, no, and no, the verdict is NO
even when Jev could technically do it.

## Step 4: Verdict and report

Write the report using `assets/verdict-template.md`. Per candidate: the
decision in one line; a verdict of **USE**, **USE WITH GUARDS**, **PILOT
FIRST**, or **NO**; why, tied to the checklist; a sketch of state, questions
(id, type, instructions, options or levels), how code combines the answers,
thresholds and where uncertain cases go; the economics lines; risks with their
guards; the best alternative and when it would win; and a concrete next step.

Keep the report proportionate; length has been the most consistent flaw in
past runs. Ceilings, including tables: a quick question 500 words; a single
decision 1,200 words; a scan or greenfield shortlist 2,500 words, with the
candidate table, 150–250 words per fit-checked candidate or proposal, and one
line per non-candidate. Being asked for "concrete" numbers does not lift the
ceiling; it means the words must be numbers, not narrative. If a draft is
over, cut in this order: restatements of how Jev works, benchmark citations
beyond one per claim, alternative sketches for candidates that are NO,
implementation notes that belong to the hand-off. The reader is a team
deciding whether to run a pilot; give them the verdict, the numbers with their
sources, the guards, and the next step.

Be precise about evidence. `references/evidence.md` separates what TypeSafe
claims from what has been measured independently. When you quote a speed or
cost multiple, say whose measurement it is. When a verdict rests on accuracy
in a domain or language nobody has measured, the verdict is PILOT FIRST, and
the pilot is specified in two steps:

1. **Smoke test, no labels needed.** Try the question wording on 10–20 real
   items in TypeSafe's Playground (https://console.typesafe.ai/playground) or
   with a 10-item `probe.py` run, and fix the wording until the answers make
   sense on reading.
2. **The pilot.** 50–200 real items, expected labels for at least half. Check
   the spec offline first, then run it:

```bash
python3 scripts/probe.py spec.json --validate
TYPESAFE_API_KEY=... python3 scripts/probe.py spec.json --repeats 3
```

`--validate` makes no API calls. It checks question types, option and level
counts, that expected labels exist among the options, and each request's
token budget, and it prints the projected cost and request count. The real
run validates again before its first call and stops on any error. The run
reports agreement with labels, the share of answers in the uncertain band,
repeat flips, p95 latency, and token usage. `assets/pilot-spec-example.json`
is a complete spec to copy (Polish marketplace listings, three Nouls and a
Choice with an `allowed` option, expected labels). If the user has no
TypeSafe key, `--openrouter` runs the same pilot through OpenRouter, and the
spec's `"model"` can then name a rival decision model (e.g. `liquid/d1`) for
the second arm.

`probe.py` calls a live API. It needs network access and `TYPESAFE_API_KEY`
or `OPENROUTER_API_KEY`, so it cannot run in a sandbox without network, such
as the Claude API's code-execution tool. If it cannot run, give the user the
spec and the two commands. Read the wrong answers one by one before setting
thresholds.

Before handing the report over, check it against itself:

```bash
python3 scripts/check_report.py report.md --kind scan   # or single | quick
```

It checks:
- that the summary's verdict counts match the sections;
- that every row of the candidate table has a section with the same verdict;
- that every proposal has a verdict;
- that no list appears twice;
- that each economics line with a dollar figure has a script run behind it;
- that the report stays under the word ceiling for its kind.

Fix every error it reports and run it again until it passes. These slips have
appeared in otherwise correct reports and cost the reader's trust.

## Hand-off

Once a candidate is USE or USE WITH GUARDS and the user wants to build it,
point them to TypeSafe's implementation skill (`claude plugin marketplace add
typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`, or `npx
skills add typesafe-ai/skills --skill typesafe-ai`) and the live docs index at
https://docs.typesafe.ai/llms.txt. Carry the sketch and thresholds from the
verdict into that work; they are the part humans most need to review, so keep
questions and thresholds in one file.

## Keeping the facts fresh

Jev launched on 2026-09-15. Its prices, rate limits, language support and
failure-mode list are all marked "may change without notice" by the vendor,
and its rate limits have already changed once. Every reference states the
date each fact was checked. Before quoting a number in a verdict, open the
live page named next to it in `references/jev-facts.md` (append `.md` to any
docs URL for Markdown). If the live page disagrees with the reference, trust
the live page and say so in the report.
