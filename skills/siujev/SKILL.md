---
name: siujev
description: >
  Decide whether and where to use Jev, TypeSafe AI's "System One" classifier
  model (typed Choice / Score / Noul answers with calibrated probabilities, no
  text generation, ~100-500 ms, $0.042 per million input tokens). Use this skill
  whenever someone asks "should I use Jev / TypeSafe for X", wants to find where
  a classifier model could replace fragile parsing, keyword heuristics, review
  queues, or LLM calls that only return a label, score, or yes/no; or needs to
  compare Jev against plain code, embeddings and rerankers, a fine-tuned small
  classifier, or a cheap LLM with structured output on accuracy, latency, cost,
  and rate limits. Also use it when a codebase, design, or product idea should
  be scanned for classification, routing, ranking, verification, detection, or
  scoring decisions, and for capabilities a fast cheap judgment makes newly
  possible (semantic conditions in code or SQL, judge-every-row columns,
  per-keystroke or per-message real-time checks, agent tool and element
  selection, context pruning, verifying another AI's steps, plain-language
  user rules), even if the user never says "Jev": "what could Jev add to our
  app", mentions of TypeSafe, System One, RLCD, "calibrated classifier API",
  or "is an LLM overkill for this classification" all qualify. Not for
  implementing the integration itself (hand off to TypeSafe's own skill) and
  not for generative tasks.
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
limits, and the nine documented failure modes. Two calibration points to hold
in mind throughout. First, accuracy: on short, bounded decisions Jev ties
mid-frontier models (GPT-5.6 Terra, Claude Sonnet 5) and the cheap flash
tier; on many-way overlapping labels it trails the frontier by 5–7 points; on
long, fuzzy, multi-field documents it trails Sol / Opus 5 / Astra / Fable 5.1
by 6–12 points, and a confidence-gated cascade recovers most of that at about
a third of the cost. Second, its typed output guarantees the *shape* of an
answer, never its correctness. Paths in this file are
relative to the skill directory.

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
- **A comparison** ("Jev vs GPT/DeepSeek/embeddings for X"): fit check, then
  `references/alternatives.md`, then economics with the specific rival.
- **A quick question** ("is it really 400x cheaper for us?"): answer it
  directly with the numbers, the source of each number, and the one or two
  caveats that change the decision. The full report format is for scans and
  for decisions someone will build on; do not pad a quick answer into one.

Do not start by praising or dismissing Jev. Start by writing down the decision
in one line: *what is judged, over what input, and what the code does with the
answer*. Most bad verdicts come from never stating this.

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
100–500 ms, sub-cent, calibrated judgment would enable something the product
does not do today. `references/use-case-catalog.md` has named examples with
numbers for each family; use it to make proposals concrete rather than
generic. This pass is where Jev has surprised people, and the one an agent
skips unless told to do it. Propose two to four new capabilities that fit the
domain, sketched like any other candidate.

Output of this step: a table, one line per candidate, in the form given in the
reference (where, what is judged, shape, current implementation or "new
capability", volume and latency context). Keep it to what you can support
with a file and line, a requirement sentence, or a stated product goal.

## Step 2: Fit check (per candidate)

Work through `references/fit-checklist.md` in order:

1. **Hard blockers.** Generation, non-enumerable answers with no candidate
   generator, arithmetic or date logic at the core, multi-hop reasoning,
   non-text input, state over 32k tokens that cannot be filtered, on-prem
   requirement, or an existing trained classifier that already meets the bar.
   Any one of these is a NO for the decision as stated. Often the decision can
   be restated so a *part* of it fits (Jev selects among regex candidates; code
   does the arithmetic; an LLM generates and Jev verifies). Say so explicitly
   rather than forcing the whole thing in or throwing the whole thing out.
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
   measurement exists for that language (see `evidence.md`); for Polish and
   other Slavic languages none does as of this writing.

Cross-check the sketch against the failure-mode table in `jev-facts.md`. The
common traps: asking Jev to count or compare numbers, feeding it dates, hiding
three judgments in one question, sending the whole document when one field
matters, and trusting it as the sole gate against hostile input. TypeSafe's own
advice is that when you find yourself explaining what you *meant* by a
question, that explanation is the missing half of the instruction.

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
context budget or the load exceeds the rate limits. `--list-presets` shows the
built-in LLM prices in two tiers. Use both, for different questions. For
**cost**, the honest rival is a cheap model in Jev's accuracy band on short
decisions (DeepSeek V4.1 Flash, Qwen 3.7/3.8 Flash, GLM-5.3 Flash, Gemini
Flash-Lite, GPT-5 nano / 5.6 Luna, Haiku 4.5), where independent tests put the
gap at roughly 3–15x per decision, not the vendor's 400x. For the **accuracy
ceiling**, name where Jev stands against the frontier tier for this task type
(`evidence.md` has the table: ties with Terra / Sonnet 5 on short crisp tasks,
5–7 points behind on 77-way intents, 6–12 behind Sol / Opus 5 / Astra / Fable
5.1 on long multi-field documents) and, when the incumbent is a frontier model
or the bar is frontier accuracy, price the cascade arm too: Jev with a 0.8–0.9
confidence gate plus the frontier model for the remainder, which has measured
at 26–37 % of the frontier cost within 1–2 points. Always also compare against
plain code or an existing trained classifier whenever one could do the job.

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
the pilot is specified: 50–200 real items, expected labels for at least half,
run with

```bash
TYPESAFE_API_KEY=... python3 scripts/probe.py spec.json --repeats 3
```

which reports agreement with labels, the share of answers in the uncertain
band, repeat flips, p95 latency, and token usage. `assets/pilot-spec-example.json`
is a complete spec to copy (Polish marketplace listings, three Nouls and a
Choice with an `allowed` option, expected labels). If the user has no TypeSafe
key, `--openrouter` runs the same pilot through OpenRouter. Read the wrong
answers one by one before setting thresholds.

Before handing the report over, check it against itself: the verdict counts
in the summary match the sections below, every candidate in the table has a
section (proposals included), no list appears twice, and every cost line
traces to a script run. These slips have appeared in otherwise correct
reports and cost the reader's trust.

## Hand-off

Once a candidate is USE or USE WITH GUARDS and the user wants to build it,
point them to TypeSafe's implementation skill (`claude plugin marketplace add
typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`, or `npx
skills add typesafe-ai/skills --skill typesafe-ai`) and the live docs index at
https://docs.typesafe.ai/llms.txt. Carry the sketch and thresholds from the
verdict into that work; they are the part humans most need to review, so keep
questions and thresholds in one file.

## Keeping the facts fresh

Jev is days old at the time this skill was written (2026-09-21). Prices, rate
limits, language support, and the failure-mode list are all marked "may change
without notice" by the vendor. Before quoting a number in a verdict, open the
live page named next to it in `references/jev-facts.md` (append `.md` to any
docs URL for Markdown). If the live page disagrees with the reference, trust
the live page and say so in the report.
