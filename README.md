# siujev — Should I use Jev?

A model that **cannot write a single sentence** became the most talked-about
release of September 2026. [Jev](https://typesafe.ai), TypeSafe AI's "System
One" model, takes a state and typed questions and answers with a choice, a
score, or a yes/no probability in a few hundred milliseconds for a few
thousandths of a cent. The pattern behind the hype: **the big model writes,
code executes, and Jev decides.**

The excitement is justified. So is the scepticism: the vendor's "444x cheaper"
is a self-tested peak, accuracy sits at mid-frontier level on short crisp
decisions and well below the frontier on long messy documents, and the API
launched on 2026-09-15 behind a waitlist with no SLA. And Jev is already not
alone: see [Jev is no longer the only choice](#jev-is-no-longer-the-only-choice).

**siujev** is an [agent skill](https://agentskills.io) for Claude Code, Codex,
Cursor, and any other coding agent. For your codebase or product idea it
answers one question: *should this decision be made by Jev, or by something
else?* It answers it the way a careful engineer would: with the shape of the
decision, the documented failure modes, measured latency and cost against the
real alternatives, a verdict, and a pilot you can run in an afternoon. It
complements TypeSafe's own [implementation skill](https://github.com/typesafe-ai/skills),
which covers *how* to build once you have decided.

## What it does

1. **Finds the decisions.** First the judgments your software already makes
   badly or expensively (keyword heuristics, regex standing in for meaning,
   LLM calls that only return a label, review queues where most items are
   fine). Then the ones it does not make at all because a judgment used to
   cost seconds and cents: a score on every row, checks on every keystroke,
   tool selection inside an agent, verification of another AI's steps, rules
   your users write in plain language.
2. **Checks each one honestly.** Hard blockers (generation, including "be the
   model behind my coding agent", arithmetic, dates, multi-hop reasoning,
   images, 32k tokens, on-prem), decision shape, the nine failure modes
   TypeSafe documents, and the traps independent audits found.
3. **Does the arithmetic.** A cost and rate-limit estimator with dated prices
   for the cheap and frontier LLM tiers, the cascade that recovers frontier
   accuracy at a third of the price, and the decision models that now take
   Jev's API.
4. **Delivers a verdict** per candidate (USE, USE WITH GUARDS, PILOT FIRST or
   NO) with a question sketch, thresholds, guards, the best alternative and a
   next step. A pilot script checks your spec offline, then runs your own
   samples through the live API and reports agreement, uncertainty, repeat
   stability and latency. Changing one field pilots a rival model with the
   same spec. A report checker catches wrong verdict counts, unsourced costs
   and runaway length before you hand it over.

Every number carries its source and the date it was checked, and the evidence
file separates what vendors claim from what others measured.

## Jev is no longer the only choice

Within three weeks of Jev's release, OpenRouter listed 27 entries (models,
aliases and tiers) that take its request format, from OpenAI, Microsoft,
Perplexity, Cloudflare, Liquid and others, and open-weight models you can host
yourself appeared on Hugging Face. This skill ran fifteen of them through the
same public sets, fresh unpublished test sets (a contamination check) and a
500-item stress test of negation, sarcasm, injected instructions and Polish
edge cases (2026-10-01 to 10-17). In short:

- **Two matched Jev even on the stress test:** OpenAI Decisions (GPT-6 Luna)
  and Perplexity Decider 27B. Perplexity costs about a fifth of Jev per
  decision; OpenAI adds image input and EU processing.
- **Several are cheaper** (Liquid D1 and Mercury about a third to a fifth of
  Jev's cost per decision) and tied or led on ordinary items, but fell behind
  on the hard ones, mostly Polish. Some look trained on a public benchmark
  (Clef).
- **Self-hosting works, at a price in accuracy:** H2O-Lightning-4B runs on a
  12 GB GPU and is the best open model measured, still behind Jev on hard
  items. Models of 26 to 31 billion parameters did not fit and were not tested.
- **Some are not ready**: low option limits (20 to 26 per Choice), weak on
  adversarial input, or Noul-only.
- **Jev moves too:** Jev 1.14 was listed on 2026-10-14; the figures here are
  for 1.13.

So the answer to "should I use Jev?" now often includes "pilot it next to
OpenAI Decisions and Perplexity". Full tables are in
`skills/siujev/references/evidence.md` (§5d to §5g) and the comparison in
`references/alternatives.md` (§2c).

## Install

Claude Code plugin:

```bash
claude plugin marketplace add maciejczub/skill-siujev
claude plugin install siujev@siujev
```

Other agents via skills.sh: `npx skills add maciejczub/skill-siujev --skill siujev`.
Manual: copy `skills/siujev/` into your agent's skills directory.

An installed plugin does not update itself, and the facts here date quickly:

```bash
claude plugin marketplace update siujev
claude plugin update siujev@siujev
```

then restart the session. The scripts need Python 3 and nothing outside the
standard library; the pilot script also needs network access and a TypeSafe or
OpenRouter API key.

## Use

Ask your agent things like:

> Should I use Jev for the ticket triage in `support/triage.py`?
>
> Scan this repo and tell me where Jev would replace fragile code or LLM calls, and what it would let us build that we can't today.
>
> We're building a marketplace for used board games. What could Jev add, what would it cost at 500 listings a day, and what should we pilot first?
>
> We do 300k intent classifications a day with DeepSeek. Someone says Jev is 400x cheaper. Is that true for us, and would it be as accurate?
>
> Compare Jev and OpenAI Decisions for live chat moderation at 50k messages a day.
>
> Can I set Jev as the model in Cursor to make my coding agent cheaper?

In Claude Code you can invoke it directly with `/siujev:siujev`.

## What is inside

```
skills/siujev/
├── SKILL.md           workflow: scan → fit check → economics → verdict
├── references/        jev-facts, fit-checklist, scan-signals, use-case-catalog,
│                      alternatives (who wins when), evidence (claims vs measurements)
├── scripts/           prices.json (single dated source of prices and limits),
│                      estimate_cost.py, probe.py (pilot, --validate), check_report.py
└── assets/            verdict template, ready-to-run pilot spec (48 Polish listings)
evals/                 six evals, fixtures and RESULTS.md
tools/check_skill.py   repository checks, also run in CI
```

## How well it works

The evals were run on Claude Haiku 4.5, Sonnet 5.5 and Opus 5.5 with the skill
and on Sonnet 5.5 without it (with web access); a separate grader checked every
expectation. Score out of 57:

| Model | Score |
|---|---|
| Sonnet 5.5 or Opus 5.5 with the skill | 54 (95 %) |
| Haiku 4.5 with the skill | 38 (67 %) |
| Sonnet 5.5 without the skill | 38 (67 %) |

The skill was chosen for all seven requests where it should be and none of the
seven where it should not, on all three models. Use Sonnet or Opus for scans
and reports; Haiku is fine for quick questions. Details and caveats are in
`evals/RESULTS.md`.

## Keeping it current

Jev shipped on 2026-09-15 and its prices, limits and failure-mode list change;
its rate limits already changed once, and new decision models appear weekly.
Every reference carries the date it was checked and the live URL to re-check.
Prices and limits were last refreshed on 2026-10-01, the benchmarks run
through 2026-10-17.

Pull requests that update numbers with a source are welcome. Change them in
`skills/siujev/scripts/prices.json` and the matching table in
`references/alternatives.md`, then run `python3 tools/check_skill.py`, which
checks that the two agree along with the skill's format rules and scripts. CI
runs the same check on every push.

## License

MIT.
