# Fit checklist: is this decision a Jev decision?

## Contents
- Outcomes (USE, USE WITH GUARDS, PILOT FIRST, NO)
- 1. Hard blockers
- 2. Decision shape
- 3. Green signals
- 4. Yellow signals (each needs a named guard)
- 4b. Design rules that decide whether the sketch will work
- 5. Economics
- 6. Verification before commitment

Run this per candidate. Work through the sections in order; the first section
can end the evaluation early. Record the outcome as one of:

- **USE**: shape fits, no blocker, economics favour Jev.
- **USE WITH GUARDS**: shape fits but at least one yellow signal needs a
  mitigation (listed in the verdict).
- **PILOT FIRST**: fit is plausible but hinges on something only data can
  settle (non-English input, adversarial traffic, subtle rubric). Name the pilot.
- **NO**: a hard blocker, or an alternative is clearly better. Name it.

## 1. Hard blockers (any one means NO for this shape as stated)

| Blocker | Why | What usually works instead |
|---|---|---|
| The output must be **generated text, code, a summary, a rewrite, an explanation** | Jev returns only typed values | LLM; or split: LLM generates, Jev verifies/selects |
| Jev would be **the model that drives a coding agent, chatbot, or other agent** (streaming text, calling tools, editing files) | Not an LLM; TypeSafe's coding-agents page says no setting makes an agent Jev-powered | Keep the LLM; use Jev *inside* the agent for routing, tool or element choice, verification; for "which LLM should answer", Jev Router or a Choice over models |
| The answer space **cannot be enumerated in advance** and candidates cannot be produced by code (regex, parser, retrieval, an LLM) | A classifier cannot choose an option the application never supplied | LLM extraction; or add a candidate generator, then re-evaluate as "selection" |
| The judgment needs **arithmetic, counting, magnitude comparison, date ordering or windows** as its core | Documented failure modes 2 and 3 | Do the math in code; use Jev only for the semantic sub-question (e.g. "which month is named?") |
| The judgment needs **multi-step reasoning, chained inference, double negation, or a property of a property** | "System Two" work; failure mode 4 | LLM with thinking; or decompose into several literal single-hop questions and combine in code |
| Input is **not text** (image, audio, video, binary) and there is no text pre-processing step | Text only | OCR/ASR/description first, then Jev on the text |
| The required state **exceeds 32k tokens** and cannot be filtered or chunked in code | Context limit; accuracy already degrades well before it | Retrieve/filter in code; map-reduce over chunks; long-context LLM |
| The system needs **on-prem / self-hosted inference** or a region guarantee the vendor does not offer | Jev is API-only (TypeSafe cloud, or via OpenRouter) | Fine-tuned open encoder (DeBERTa/ModernBERT/SetFit), local reranker, open-weight LLM |
| A **mature labeled dataset already exists** and a trained classifier already meets the bar | Jev's value is skipping training; it is not free per call | Keep the trained model; consider Jev only for new labels or drift |

## 2. Decision shape (find the row; if none fits, it is probably not a Jev job)

| Shape | Typical question | Primitive | Pattern to reuse |
|---|---|---|---|
| Classification | which one of N categories | Choice (+ `other`) | intent routing; hierarchical classification for deep taxonomies |
| Detection | is property X present | Noul per property | guardrails, PII, urgency, spam signals |
| Scoring | where on an ordered rubric | Score (2–10 described levels) | composite scoring (one dimension per Score) |
| Routing | which handler / model / queue | Choice + Score(complexity) + confidence gate | intent routing, model routing |
| Ranking / reranking | order candidates by relevance | one Noul or Score per candidate, sort in code | rerank cookbook; bounded shortlist |
| Search over a document | which line/section matches | Choice over line ids + Noul "is there an answer at all" | line-by-line search |
| Verification | does artifact satisfy check K | Noul per check | citation check, tool-call trace check, LLM output guard |
| Extraction by selection | which candidate span is the value | Choice over regex/parser candidates + `not_stated` | pre-parsed value extraction, date extraction |
| Entity matching / dedup | are these two records the same | Noul per pair, or Score(merge/unlinked/review) | entity alignment |
| Feature extraction for ML | probability of semantic feature | Noul/Score per feature, feed into classical model | autoresearch feature discovery |
| Pre-filter before an LLM | is this input relevant / hard / risky | Noul + Score, then route | SDE cascade, RAG passage classification |

Questions that do not decompose into these shapes (open-ended analysis, "figure
out what to do", planning) belong to an LLM or an agent.

## 3. Green signals (each one strengthens USE)

- The judgment is a **snap call a domain expert makes in seconds** given the right context.
- It is **currently done by fragile code**: keyword lists, regex heuristics, hand-tuned scores, `if "refund" in text`.
- It is **currently done by an LLM call whose output is parsed into a label, boolean, or score**, and the prompt does no generation.
- It sits on a **hot path** where 1–3 s of LLM latency hurts (request handling, UI, real-time streams).
- **Volume is high** (tens of thousands of items per day and up) so per-call cost matters.
- Several **independent judgments are needed on the same input** (fan-out makes them nearly free).
- A **probability or confidence is actionable**: there is a human review queue, a fallback model, or a threshold to tune against outcomes.
- The input is **English** or the team can pilot on its real language.
- The options are **stable and describable** with a sentence and an example each.

## 4. Yellow signals (fit is possible; each needs a named guard)

| Signal | Guard |
|---|---|
| Inputs are mostly **non-English** | Pilot on 100+ real items; compare accuracy against an LLM; keep confidence gates tight. Known data: Korean calibration parity, a German injection corpus at 96.5 %, and this skill's two small synthetic Polish sets (Jev: listing Nouls 92–100 %, support-ticket Nouls 99 %, checked 2026-10-01); nothing on long or messy non-English text |
| **Adversarial** traffic (user-submitted content that may argue for its own label or inject instructions) | Precise criteria; second independent check (LLM or rules); never let Jev be the sole gate for a security decision |
| Very **long or noisy state** (5k+ tokens with distractors) | Filter/retrieve in code first; or a two-stage pass: Noul relevance filter, then the real question |
| Options are **subtle or overlapping** | Structured criteria with `what` / `not_for` / `examples`; expect low confidence on boundary cases and route them to review |
| The judgment **depends on world knowledge** rather than the state | Put the reference material in the state; do not rely on model weights |
| **Thresholds drive automatic irreversible actions** | Tune on labeled data; use higher confidence for irreversible actions; pin the model version |
| **Rate limits**: peak load near 40 req/s or 100k tokens/s (published 2026-10-01; were 1,200 req/min and 250k tokens/s at launch) | Batch questions per request; queue; ask sales for higher limits |
| The team needs **explanations** for each decision (audit, appeals) | Jev gives none; log the decomposed question answers as the explanation, or add an LLM to explain flagged cases only |
| **Vendor risk**: a startup product launched 2026-09-15, limits "adjusting dynamically" (already changed once) | Wrap calls behind an interface with a fallback; pin versions; plan for outages. Since late September other decision models take the same request body (Liquid D1, Mercury Decide), so the fallback can be a `model` swap; pilot it and tune its thresholds separately |
| **Long candidate lists** to rerank (dozens to hundreds per query) | The 32k ceiling forces one request per candidate, which erases the latency edge; pre-filter in code to ≤ 30, or use a dedicated reranker or a cheap-tier LLM |
| **Long, fuzzy single-shot judgment** (e.g. "is this whole email phishing?") | Jev trailed Haiku 63 % vs 81 % on that; decompose into 4–6 narrow signals and combine in code or with a small regression on labelled data |

## 4b. Design rules that decide whether the sketch will work

These come from TypeSafe's cookbooks and from independent audits; a candidate
whose sketch violates one of them will underperform in the pilot.

- **Keep the floor.** A rules engine, keyword list or human queue that
  already works stays as an independent signal in front of or beside Jev.
  Jev replaces the expensive or brittle part, not the safety floor, and
  disagreements between the two go to review.
- **Never auto-act inside the uncertain band.** With a human queue, automatic
  actions start above the band (TypeSafe's 0.85–0.9+ for irreversible ones),
  and everything between the floor and that threshold goes to people.
- **Always give an out.** A Choice always ranks something first; add
  `none` / `other` / `not_stated`, or pair it with a Noul "is there an answer
  at all". An audit found accuracy on unanswerable items going from 95 % to
  0 % when the `unknown` option was removed.
- **Decompose.** One question per checkable fact; the cookbooks' per-field
  verifier Nouls separated errors at 0.85–0.95 where a holistic "is this
  good?" gave 0.56, and an independent phishing test went from 62.6 % (one
  question) to 95 % (five questions plus a small regression on labelled data).
- **Batch questions, not items.** Sixteen questions over one state changed
  answers by 0.4 %; packing 40 items to rank into one state dropped rank
  correlation from 0.93 to 0.58. To rank N candidates, send N requests with the
  same question (or a Choice over ids for "which line", not for ordering).
- **Frame Nouls so true = act**, and never invert (true means no).
- **Gate on `confidence`** (distribution shape) for Choice/Score, on the
  probability band for Noul; use a review band, not a single cut, when a human
  queue exists. Composite confidence = min over parts; escalation = max over
  flags.
- **Probabilities have two decimals.** Ties at 0.99 are common; do not use a
  bare sort of probabilities as a fine-grained ranking of near-equals.
- **Expect wording sensitivity.** A rewording changed 17 vs 12 recovered
  blocks in one cookbook; keep questions and thresholds in one reviewed file
  and re-run the pilot after changing either.
- **Option lists**: hard cap 255; about 240 reported reliable; beyond that,
  chunk and rerank in two stages.
- **Concurrency**: cookbooks used 4–12 threads; one reports throttling above
  ~8 concurrent calls on a shared key. Plan a queue.

## 5. Economics (numbers decide between USE and "not worth it")

Run `scripts/estimate_cost.py` with measured token counts. Then ask:

- Is the per-item cost of the incumbent (LLM, human, or engineering time on
  heuristics) higher than Jev's by a margin that pays for integration and a
  pilot? A migration from an LLM classifier usually is, when volume is high; a
  migration from ten lines of working regex usually is not.
- Does latency change the product? If the incumbent is an async batch job that
  already finishes overnight, Jev's speed buys little. If the decision is in a
  request path, it may buy a feature.
- Does calibration change the operations? If nobody will act on probabilities
  (no review queue, no thresholds), one of Jev's main advantages is unused.

## 6. Verification before commitment

A USE verdict on anything user-facing or irreversible should be followed by a
pilot, in two steps. First a smoke test without labels: 10–20 real items in
TypeSafe's Playground or a 10-item `scripts/probe.py` run, to fix the question
wording. Then the pilot: 50–200 real items, expected labels for at least half,
`scripts/probe.py --validate` to check the spec offline, then
`scripts/probe.py` with `--repeats 3`. Look at agreement, the share of answers
in the uncertain band, repeat flips, and p95 latency. Read the wrong answers
individually. Only then set thresholds, separately for every model piloted.
