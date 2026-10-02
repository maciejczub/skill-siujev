# siujev — Should I use Jev?

Something unusual happened in the week after 15 September 2026. A model that
**cannot write a single sentence** became the most talked-about release of
the year. [Jev](https://typesafe.ai), TypeSafe AI's "System One" model, takes a
state and typed questions and answers with a choice, a score, or a yes/no
probability in a few hundred milliseconds for a few thousandths of a cent.
Within days people had it playing Doom from emulator memory, driving a
browser agent that books flights for $0.004, pruning Claude Code's context
without rewriting a byte, judging 1,018 research papers for eight cents,
filtering a social feed as you scroll, and answering `WHERE jev(people,
'could work from home')` inside Postgres. Over 1,300 public builds in the
first week, and the pattern is always the same: **the big model writes, code
executes, and Jev decides.**

The excitement is justified. So is the scepticism: the vendor's "444x cheaper"
is a self-tested peak, the accuracy sits at GPT-5.6 Terra level on short
crisp decisions and well below the frontier on long messy documents, and the
API launched on 2026-09-15 behind a waitlist with no SLA. Within two weeks it
also had rivals that take the same API. The gap between "this is a
new primitive" and "this is the right primitive for *my* feature" is exactly
where projects burn time.

**siujev** closes that gap. It is an [agent skill](https://agentskills.io) for
Claude Code, Codex, Cursor, and any other coding agent that answers, for
your codebase or your product idea, one question: *should this decision be
made by Jev?* And it answers it the way a careful engineer would: with the
shape of the decision, the documented failure modes, measured latency and
cost against the models Jev actually competes with, a verdict, and a pilot
you can run in an afternoon.

## What it does

1. **Finds the decisions.** Two passes over a repo, a design, or a feature
   request. First the judgments your software already makes badly or
   expensively: keyword heuristics, regex standing in for meaning, LLM calls
   whose output is a label, review queues where most items are fine. Then
   the judgments it does not make at all, because until now a judgment cost
   seconds and cents: semantic conditions inside ordinary code, a score on
   every row of a table, checks on every keystroke or chat message, tool and
   element selection inside an agent, verification of every step another AI
   takes, rules your users write in plain language. A catalog of what people
   have built, by capability family and with their numbers, keeps the
   proposals concrete.
2. **Checks each one honestly.** Hard blockers (generation, including "be
   the model behind my coding agent", arithmetic, dates, multi-hop reasoning,
   images, 32k tokens, on-prem), decision shape, the
   nine failure modes TypeSafe itself documents, and the traps independent
   audits found: no `none` option, packing items to rank into one state,
   trusting it as a security boundary.
3. **Does the arithmetic.** A cost and rate-limit estimator with current
   prices for the cheap tier Jev competes with on cost (DeepSeek Flash, Qwen,
   GLM, Gemini Flash-Lite, GPT-6 Luna) and the frontier tier it competes
   with on accuracy (GPT-5.6 Terra and Sol, GPT-6 Sol and Astra, Claude
   Sonnet 5.5, Opus 5.5 and Fable 5.1), including the cascade that gets
   frontier accuracy at a third of the price. It also covers the decision
   models that now take Jev's exact API (Liquid D1, Mercury Decide, Solar
   Decide, Tev1, Kev 4B, Span-01), benchmarked head to head against Jev. The
   short version: Liquid D1 matched Jev on ordinary items at about a third
   of the cost per decision, and Jev was the most robust on a stress test of
   traps (negation, sarcasm, injected instructions, Polish edge cases).
4. **Delivers a verdict** per candidate: USE, USE WITH GUARDS, PILOT FIRST,
   or NO, with a question sketch, thresholds, guards, the best alternative,
   and a next step. A bundled pilot script checks your spec offline, then
   runs your own samples through the live API (directly or via OpenRouter)
   and reports agreement, uncertainty, repeat stability, and latency before
   you commit. The same spec pilots a rival decision model by changing one
   field. A second script checks the finished report against itself: verdict
   counts, cost provenance, length.

Every number in the skill carries its source and the date it was checked, and
the evidence file separates what TypeSafe claims from what others measured,
including a small Polish-language pilot run for this skill because nobody
else had measured one, and a benchmark of seven decision models plus a cheap
LLM, with a contamination check on fresh, deliberately unpublished test sets
and a 500-item stress test built on the models' documented failure modes.

It complements TypeSafe's own
[implementation skill](https://github.com/typesafe-ai/skills), which covers
*how* to build once you have decided.

## Install

Claude Code plugin:

```bash
claude plugin marketplace add maciejczub/skill-siujev
claude plugin install siujev@siujev
```

Other agents via skills.sh:

```bash
npx skills add maciejczub/skill-siujev --skill siujev
```

Manual: copy `skills/siujev/` into your agent's skills directory.

Update an installed Claude Code plugin (the facts in this skill date quickly,
and an installed copy does not update itself):

```bash
claude plugin marketplace update siujev
claude plugin update siujev@siujev
```

Then restart the session. The scripts need Python 3 (tested on 3.12) and
nothing outside the standard library; the pilot script also needs network access and
a TypeSafe or OpenRouter API key.

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
> Compare Jev and Liquid D1 for live chat moderation at 50k messages a day.
>
> Can I set Jev as the model in Cursor to make my coding agent cheaper?

In Claude Code you can invoke it directly with `/siujev:siujev`.

## What is inside

```
skills/siujev/
├── SKILL.md                     workflow: scan → fit check → economics → verdict
├── references/
│   ├── jev-facts.md             capabilities, limits, prices, failure modes (dated)
│   ├── fit-checklist.md         blockers, decision shapes, green/yellow signals, design rules
│   ├── scan-signals.md          how to find candidates: replacement pass and opportunity pass
│   ├── use-case-catalog.md      what people build with Jev, by capability family, with numbers
│   ├── alternatives.md          cheap tier, frontier tier, rival decision models, rerankers,
│   │                            self-hosting: who wins when
│   └── evidence.md              vendor claims vs independent measurements, incl. this skill's
│                                own Polish pilot, decision-model benchmark and stress test
├── scripts/
│   ├── prices.json              single dated source of prices, limits and latencies
│   ├── estimate_cost.py         cost, latency and rate-limit estimate vs LLM presets
│   ├── probe.py                 live pilot on your data (TypeSafe API or OpenRouter);
│   │                            --validate checks a spec offline first
│   └── check_report.py          checks a report against itself before hand-over
└── assets/
    ├── verdict-template.md      report format
    └── pilot-spec-example.json  ready-to-run probe.py spec (48 Polish listings)
evals/                           six evals, fixtures, and RESULTS.md
tools/check_skill.py             repository checks, also run in CI
```

## How well it works

The evals in `evals/` were run on Claude Haiku 4.5, Sonnet 5.5 and Opus 5.5 with the
skill, and on Sonnet 5.5 without it (with web access). A separate grader checked
every expectation. Final scores out of 57 expectations:

| Model | Score |
|---|---|
| Sonnet 5.5 with the skill | 54 (95 %) |
| Opus 5.5 with the skill | 54 (95 %) |
| Haiku 4.5 with the skill | 38 (67 %) |
| Sonnet 5.5 without the skill | 38 (67 %) |

The skill was chosen for all seven requests where it should be and none of the
seven where it should not, on all three models. Use Sonnet or Opus for scans and
reports; Haiku is fine for quick questions. Details, caveats and what the runs
changed are in `evals/RESULTS.md`.

## Keeping it current

Jev shipped on 2026-09-15 and its prices, limits, and failure-mode list change;
its rate limits changed within two weeks of launch. Every reference file
carries the date it was checked and the live URL to re-check. Prices and limits
were last refreshed on 2026-10-01 and the benchmarks run on 2026-10-01 and
2026-10-02.

Pull requests that update numbers with a source are welcome. Prices, limits and
latencies live in `skills/siujev/scripts/prices.json`; change them there and in
the matching table of `references/alternatives.md`, then run

```bash
python3 tools/check_skill.py
```

which checks that the two agree, along with the skill's format rules and the
scripts. CI runs the same check on every push.

## License

MIT.
