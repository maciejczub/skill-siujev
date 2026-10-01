# Jev fact sheet (jev-1.13, verified 2026-09-21; limits and access re-checked 2026-10-01)

Everything here comes from docs.typesafe.ai unless marked otherwise. Numbers change:
before quoting a price, limit, or latency in a recommendation, re-check the live
page named in each section (Markdown versions exist at the same path with `.md`
appended, e.g. `https://docs.typesafe.ai/models.md`).

## What it is

- Jev is a **System One model** from TypeSafe AI (San Francisco, founded 2024;
  released in limited early access 2026-09-15). Model id `jev-1.13.0`, aliases
  `jev-latest` and `jev-preview` (both currently resolve to 1.13.0).
- It is a **general classifier, not a language model**. You send a `state`
  (string, JSON object, or array of text) plus a map of typed questions, and get
  back typed answers with probabilities. It never generates text, code, or
  explanations.
- Trained with "RLCD" (reinforcement learning for calibrated decisions) on
  synthetic data; transformer-based. Architecture, weights, and a technical paper
  are not published. Calibration is a population property: it does not make any
  single answer correct.
- Not fine-tunable. Same weights for every account. You adapt it through the
  request only: state content, `instructions`, `criteria`, and decomposition in
  code.
- Not trained on customer requests. Zero data retention (ZDR) is available for
  enterprise customers; a DPA and privacy policy exist (`/legal`).

## The three primitives (`/primitives`, `/api`)

| Primitive | Question shape | Returns | Limits |
|---|---|---|---|
| **Choice** | pick one option from a fixed set | `choice`, `probabilities` (sum to 1), `confidence` | up to 255 options per question |
| **Score** | position on an ordered rubric | `score` (expectation, may be fractional), `legend`, `probabilities`, `confidence` | 2 to 10 levels |
| **Noul** | is this statement true? | `noul` in [0,1] | no separate `confidence` |

- Every question in a request is evaluated **in parallel and independently**
  against the same state. Adding questions barely changes latency and costs
  only the tokens of the added question.
- `instructions` and `criteria` may be strings or JSON objects/arrays (e.g.
  `{what, not_for, examples}` per option). Question ids are not sent to the
  model.
- Questions can point at parts of a JSON state with backticked paths such as
  `` `ticket.messages[0].text` ``.
- Choice is **relative** (which option wins); Noul is **absolute** (can be low
  for all). To "pick one, or none", pair a Choice with a Noul or add an explicit
  `none`/`other`/`not_stated` option.
- No structural invariants across questions: a Noul and a yes/no Choice on the
  same question give different numbers, and P(A) + P(not A) does not sum to 1.
  Thresholds tuned on one question type do not transfer to another.

## Limits, price, throughput (`/models`, `/api`)

| Item | Value (2026-10-01) |
|---|---|
| Price | **$0.042 per million input tokens** ($42 per billion). Output tokens are free. Unchanged since launch |
| Rate limits | 100,000 tokens/s and 40 requests/s (2,400/min) per account; "adjusting dynamically" and may change without notice; higher on custom/enterprise plans. Changed after launch: on 2026-09-21 the page said 250,000 tokens/s and 1,200 requests/min, so the token ceiling fell 2.5x and the request ceiling doubled |
| Context | 64k tokens per request (state + all questions); 32k for state + the single longest question |
| Input | Text only. No images, audio, video, or binaries: pre-process to text in code |
| Languages | English is the primary training language; others (incl. CJK) are "handled but not equally well"; test before relying on it |
| Endpoint | `POST https://api.typesafe.ai/v1/systemone`; `GET /v1/models` |
| SDKs | Python `typesafe_sdk` (Python >= 3.10), JavaScript `@typesafe-ai/sdk`; env var `TYPESAFE_API_KEY` |
| Errors | 401 auth, 422 validation, 429 rate limit, 529 overloaded; SDKs retry with backoff and honor `retry-after` |
| Console | https://console.typesafe.ai (keys, playground) |
| Access | Direct API was waitlist-gated at launch (2026-09-15). Also served through Vercel AI Gateway, OpenRouter and Cloudflare AI without a waitlist. On OpenRouter the model is `typesafe/jev-1.13` (32k context, same price; endpoint snapshot `jev-1.13-20260917`, still current on 2026-10-01; it does not appear in OpenRouter's `/api/v1/models` list, so check it at `/api/v1/models/typesafe/jev-1.13/endpoints`) on a dedicated endpoint `POST https://openrouter.ai/api/alpha/decisions` that takes the native TypeSafe body (`state`, `questions`, `model`) and returns the native answers plus `id`, `provider`, and `usage.cost`; the chat-completions endpoint rejects it with a 400. `scripts/probe.py --openrouter` uses it |
| Hosting | US-hosted, multi-region. No EU residency option found, no SLA published, no on-prem, no open weights |
| Determinism | Not deterministic across identical requests; no prompt caching; Choice is single-select (use one Noul per label for multi-label) |
| Integrations | LangChain `langchain-typesafe`, Pydantic AI `TypeSafeModel`, LiteLLM, community SDKs (Go, Java, PHP, Ruby, Rust, .NET, Elixir). TypeSafe's `system-one-adapter-python` gives the same client interface backed by an LLM, usable as a fallback |

Latency, as stated by TypeSafe (no independent benchmark found as of writing):
"most queries complete in about 100 ms" (`/concepts/how-to-build-with-system-one`),
"real-time speeds (150ms)" (`/concepts/use-case-map`), "70 to 500 milliseconds
end-to-end" (press, citing TypeSafe). Treat 100–500 ms as the planning range and
measure your own p50/p95 with `scripts/probe.py`.

Speed and cost claims versus frontier LLMs are **self-tested by TypeSafe**:
"40–200x faster and 40–400x cheaper", peak 193.6x / 444.6x on workflows written by
its own model-capabilities team, which TypeSafe says likely sit at the high end of
real-world results. Use them as an upper bound, not a plan.

## Known failure modes (`/model-jaggedness/jev-1.13`, reviewed 2026-09-17)

| # | Failure mode | What to do instead |
|---|---|---|
| 1 | **Literal reading**: answers the words written, not the intent; scoping words, negations, implied conditions taken at face value | Write the exact condition; put boundary cases in `criteria`; split interpretation into two literal questions |
| 2 | **Math and numbers**: cannot count, add, compare magnitudes; weak on hex/RGB, low-level code; Score is not a number line for exact values | Compute in code; one Noul per item then sum in code; pass named buckets instead of raw numbers |
| 3 | **Dates and times**: reads dates as text; cannot order, diff, or window them | Extract components as Choice (month/day/year with `not_stated`); compare in code |
| 4 | **Indirection**: double negatives, multi-hop, "property of a property" | Direct questions; name the state path |
| 5 | **Large state with irrelevant detail**: accuracy falls with distractors (context rot) | Filter/retrieve in code first; or a Noul relevance pass |
| 6 | **Adversarial content**: injected instructions or self-arguing text can move answers; state is not treated as hostile | Precise criteria; test edge cases; do not make Jev the only defence |
| 7 | **Contradictory instructions vs criteria**; inverted Nouls (true means no) | Align wording; keep true = yes |
| 8 | **No structural invariants** between question types or between a question and its negation | Word each question for what you want; never carry thresholds across types |
| 9 | **Generation**: cannot produce text; chaining Choices to "generate" is slow and poor | Generate candidates with regex/parser/LLM; let Jev select |

TypeSafe's own summary of what to avoid: asking what code can compute exactly;
hiding several judgments in one question; "System Two" tasks with layers of
indirection; sending more state than the question needs.

## Design doctrine TypeSafe expects you to follow (`/concepts/how-to-build-with-system-one`)

1. Keep control flow, deterministic rules, arithmetic, lookups, and side effects in code.
2. Send only the context a question needs; structure state as named JSON fields.
3. Decompose broad judgments into atomic questions a knowledgeable person could answer in a second.
4. Ask all independent questions in one request (speculative fan-out). A second request is only justified when the first answer is needed to build the next state or option set.
5. Combine answers in code (weights, thresholds) or feed probabilities into a classical ML model.
6. Route on uncertainty with thresholds scaled to the stakes (typical floor 0.5–0.6; high-stakes automatic actions 0.85–0.9+). Thresholds must be tuned on your own data.
7. Pin the versioned model id if thresholds are tuned; aliases move on release.

## Where TypeSafe says it fits (`/concepts/use-case-map`)

Decision shapes: classification, detection, scoring, routing, search, retrieval,
ranking, verification, ML feature extraction, structured extraction **by
selection among candidates**. Headline categories: AI automation software,
real-time applications, map-reduce over big text corpora, universal verification
of other AI outputs (guardrails, citation checks, tool-call checks), and harness
engineering (model routing, context selection).

## Jev and coding agents (`/introduction/coding-agents`, added after 2026-09-21)

TypeSafe added this page for people who found Jev while looking for a model
to put behind Claude Code, Cursor, opencode, Copilot, or similar tools. Its
answer: Jev is **not** a drop-in replacement for a coding agent's LLM. It
does not stream text, call tools, or edit files, and no `model: "jev-latest"`
setting turns a coding agent into a Jev-powered one. The coding agent stays
an LLM; it writes code that *calls* Jev wherever the product needs a fast,
calibrated, typed decision. TypeSafe's redirects, in its own order:

| The person wanted to... | TypeSafe's answer |
|---|---|
| make the coding agent better at writing code that uses Jev | install TypeSafe's agent skill (see below) |
| use Jev inside an app or agent for routing, classification, scoring, guardrails | Quick start, then `/concepts/how-to-build-with-system-one` and `/patterns` |
| replace the model that powers a coding agent | not a Jev job; keep the LLM |
| try Jev before writing code | the Playground at https://console.typesafe.ai/playground |

The page's own "when Jev is worth reaching for" list is routing to a fixed
set of destinations with a confidence, scoring on a rubric and branching on
the number, checking whether a statement holds before an action, and
replacing a prompt that asks an LLM to "return JSON" with typed values by
construction. Typed values guarantee the shape of the answer, not that it is
correct.

**Jev Router** (`typesafe/jev-router` on OpenRouter, listed 2026-09-25) is the
one place where Jev sits in a model slot. It is an LLM *router*, not Jev: it
serves OpenRouter's chat-completions endpoint (accepts `messages`, `tools`,
`reasoning_effort`, streaming) and uses Jev to pick the model and reasoning
effort for each request. OpenRouter lists no fixed per-token price for it; the
cost is that of the routed model, reported per request in `usage.cost`. The
list of models it routes to and any quality benchmark were not published on
OpenRouter as of 2026-10-01. So "can I use Jev as my coding agent's model?" is
NO, while "can Jev pick which LLM my agent calls?" is a routing question that
Jev Router or a self-built Choice over models answers.

## Official agent skill

TypeSafe publishes an implementation skill (`claude plugin marketplace add
typesafe-ai/skills`, then `claude plugin install typesafe@typesafe-ai`; or
`npx skills add typesafe-ai/skills --skill typesafe-ai`). It covers *how* to
build once you have decided to use Jev. This skill (siujev) covers the *whether*
and *where*; hand off to the official skill for implementation details and the
live docs index at https://docs.typesafe.ai/llms.txt.
