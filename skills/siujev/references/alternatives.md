# Alternatives: what else does the job, and when it wins

## Contents
- Intro: the two tiers, decision models, where the numbers come from
- 1. The option ladder
- 2. Cheap tier (cost rivals) and per-decision arithmetic
- 2b. Frontier tier (accuracy ceiling)
- 2c. Other decision models (same request body as Jev; where to compare them)
- 2d. Superseded models kept because measurements used them
- 3. Rerankers and classification services
- 4. Self-hosted encoder
- 5. Decision rules

Compare Jev against two tiers of LLMs, for two different reasons. For
**cost**, the honest rival is the **cheap tier** (GLM-5.3 Flash, Qwen3.8 Flash,
DeepSeek V4.1 Flash, Gemini Flash-Lite, GPT-6 Luna at no or low reasoning,
Claude Haiku 4.5). On short bounded decisions Jev's accuracy sits in that band
or above it, and its cost advantage there is 3–15x per decision, not the
vendor's 400x. For the **accuracy ceiling**, show the **frontier tier**
(GPT-5.6 Terra, GPT-6 Sol / 6.1 Sol / Astra, Claude Sonnet 5.5 / Opus 5.5 /
Fable 5.1, Gemini 3.8 Flash).

Most published comparisons ran on the models current in mid-September:
Terra, Sonnet 5, Opus 5, GPT-5.6 Sol, Astra and Fable 5.1. Their successors,
released 2026-09-21 to 09-29, are in no independent comparison yet, apart from
GPT-6 Luna in this skill's own benchmark. For a successor, quote the gap
measured against its predecessor and plan as if it is at least as large.

What those comparisons show:
- On short crisp tasks Jev ties Terra and Sonnet 5 (−2 to +1 points; it beat
  Terra 89 vs 88 on 100k AG News rows).
- It trails Terra by 5–7 points on 77-way overlapping intents.
- It trails Sol / Opus 5 / Astra / Fable 5.1 by 6–12 points on long, fuzzy,
  multi-field documents (17 points on invoices in the vendor's own eval).
- A confidence-gated cascade (Jev first, frontier model for the uncertain
  20–37 %) lands within 1–2 points of the frontier model at 26–37 % of its
  cost. Gate at a confidence of about 0.8–0.9.

Also compare against a self-hosted encoder, against plain code, and, since
late September 2026, against other decision models that take Jev's exact
request body (§2c).

Prices are in USD per million tokens, checked 2026-09-21 and re-checked
2026-10-01 on vendor pages and OpenRouter. The script's copies live in
`scripts/prices.json`; the skill repository's CI checks that both agree. Prices move monthly, so re-check the source before quoting. "OR p50"
is OpenRouter's median latency over a 30-minute window on 2026-09-21, a rough
indicator only; "measured" means this skill's own runs on 2026-10-01. OpenAI's
pricing page lists service tiers (Batch and Flex at 50 % of standard, Fast at
2x, Ultrafast at 6x for GPT-6 Astra only); the tables show standard prices.

## 1. The option ladder

Work down this ladder and stop at the first rung that meets the bar.

| Rung | When it wins | Cost order | Latency |
|---|---|---|---|
| **Plain code** (regex, parser, lookup, rules) | The condition is lexical or structural and stable; you can enumerate it | ~0 | µs |
| **Existing trained classifier** (TF-IDF+LR, DeBERTa, SetFit) | You already have thousands of labels and a model that meets the bar; a spam test showed Jev zero-shot 98.3 % vs TF-IDF+LR on 14.8k labels 98.4 % | GPU/CPU rent, idle cost | 1–40 ms |
| **Jev** (or another decision model with the same API, §2c) | Judgment needs meaning, not lexical match; labels are few or shifting; you want calibrated probabilities and sub-second latency without training | $0.042/M input, output free (several rivals that tied Jev cost a fifth to a third as much per decision) | 100–500 ms (independent p50 240–385 ms) |
| **Cheap LLM with structured output** | Same as Jev but you also need short generation, longer or messier inputs, or tasks where Jev measurably trails (long fuzzy single-shot judgments, 77-way intents) | $0.03–0.30/M in, $0.13–1.20/M out | 0.4–2 s (up to 5–15 s if reasoning is on by default) |
| **Frontier LLM** | Multi-step reasoning, generation, or the extra accuracy pays for itself (invoice-type extraction: vendor eval 79 % vs Jev 62 %) | $1–10/M in, $5–50/M out | 2–40 s |
| **Human** | Stakes or ambiguity exceed any model; use Jev to shrink the queue, not to empty it | $ per item | minutes to days |

## 2. Cheap tier (cost rivals; checked 2026-09-21, re-checked 2026-10-01)

| Model | $/M in | $/M out | OR p50 latency | Notes |
|---|---|---|---|---|
| Qwen3.7 Flash (Alibaba, ≤32k input) | 0.03 | 0.13 | 738 ms | Cheapest hosted rival; beat Jev on cost in one independent test, lost on accuracy in that test (82–95 % vs 95–100 %) |
| Amazon Nova Micro | 0.035 | 0.14 | 376 ms | Fast and cheap, weak model, text only |
| Mistral Nemo 12B (DeepInfra) | 0.019 | 0.03 | 475 ms | 2024 model, weak; open weights |
| Qwen3-30B-A3B (open, cheapest host) | 0.048 | 0.19 | ~1.1 s | Self-host candidate |
| GPT-5 nano | 0.05 | 0.40 | 1.3 s | Reasoning on by default |
| GPT-6 Luna (OpenAI, released 2026-09-22) | 0.10 | 0.50 | measured 1.2 s (reasoning none) | Successor of GPT-5.6 Luna at half its price; Flex 0.05 / 0.25. In this skill's benchmark (2026-10-01) it tied Jev on accuracy except star scoring, cost 1.4–2.5x Jev per decision, returned no probabilities to gate on |
| Gemini 2.5 Flash-Lite | 0.10 | 0.40 | 386 ms | Highest-volume cheap model on OpenRouter; native JSON schema |
| Ministral 3B / 8B | 0.10 / 0.15 | 0.10 / 0.15 | 304 / 346 ms | Latency peers of Jev; Mistral also sells a Classifier API (8B) at 0.04 / 0.04 |
| ByteDance Seed 2.0-mini | 0.10 | 0.40 | 371 ms | Fastest Chinese model measured |
| Qwen3.8 Flash | 0.15 | 0.47 | 5.0 s default, ~0.7 s with reasoning low | DevX ticket routing 90 % |
| GLM-5.3 Flash (Z.ai) | 0.15 (0.075 on DeepInfra) | 0.50 | 3.2 s default, ~0.9 s low | DevX 94–95 %, best of the sub-$0.20 tier on the AA index |
| DeepSeek V4.1 Flash (first-party) | 0.15 off-peak / 0.30 peak | 0.60 / 1.20 | 2.9 s default, ~1.7 s low | DevX 97 % (statistical tie with Jev at n=100); cache hits ~0.003. Some of the ~30 third-party hosts on OpenRouter charge as little as 0.03 / 0.50, on par with Jev's input price; check the host's quantisation and latency before treating that as the rival price |
| Mistral Small 4 | 0.15 | 0.60 | 416 ms | Measurably worse than Jev in two tests (79–86 %) |
| StepFun 3.7 Flash | 0.16–0.20 | 0.92–1.15 | 362 ms | Fast |
| Gemini 3.1 / 3.5 Flash-Lite | 0.25 / 0.30 | 1.50 / 2.50 | 0.5 / 1.2 s | 3.5 had the worst calibration in the Supa test (ECE up to 0.16) |
| MiniMax M2.7 / M3 | 0.30 | 1.20 | ~1.7 s | |
| Kimi K2.6 | 0.95 (0.41 via Baidu on OR) | 4.00 | 1.1 s | Not cheap at first-party price; K2.5 retired 2026-08-31 |
| Claude Haiku 4.5 | 1.00 | 5.00 | 0.8 s | Beat Jev on single-question phishing (81 vs 63 %); 12–27x Jev's cost |

Per-decision arithmetic that matters more than the per-token price:

- A Jev request bills the state once plus ~30–50 tokens per question; an LLM
  prompt carries instructions plus the content and pays for output tokens. In
  independent tests Jev used 85 tokens where the LLM prompt used 910 for the
  same decision, so Jev's per-decision advantage over a cheap-tier LLM is
  usually 3–15x, not the vendor's 400x. Against Qwen3.7 Flash it can be a loss.
- Reasoning-default models (DeepSeek, GLM, Qwen 3.8, GPT-5.6, GPT-6.1 Sol) must be run with
  reasoning at its lowest setting for classification; otherwise cost triples
  and latency reaches 3–15 s.
- Batch tiers (OpenAI, Google, Mistral) halve LLM prices for offline jobs;
  Jev has no batch discount but also no output charge.
- Jev's 32k state ceiling forces one request per passage when reranking long
  lists; in a 100-chunk RAG rerank the cheap-tier LLMs did slightly better at
  a similar cost and Jev lost its latency edge (6.8 s per question for 100
  calls). Rerank short lists, or pre-filter in code.

## 2b. Frontier tier (accuracy ceiling; checked 2026-09-22, re-checked 2026-10-01)

| Model | $/M in | $/M cached in | $/M out | p50, short classification | Where Jev stands |
|---|---|---|---|---|---|
| GPT-5.6 Terra (OpenAI) | 2.00 | 0.20 | 12.00 | ~1.0–1.5 s (independent) | tie on short crisp tasks; −5–7 on 77-way intents |
| GPT-6 Sol (OpenAI, released 2026-09-22) | 2.00 | 0.20 | 10.00 | measured 1.5 s (reasoning none) | no published comparison; successor of GPT-5.6 Sol (§2d) |
| GPT-6.1 Sol (OpenAI, released 2026-09-29) | 2.00 | 0.10 | 10.00 | measured 2.7 s (reasoning low; none is rejected) | no published comparison |
| GPT-6 Astra (OpenAI) | 10.00 | 1.00 | 50.00 | not measured | −6.5 on a 200-item mixed set |
| Claude Sonnet 5.5 (released 2026-09-28) | 2.00 | 0.20 | 10.00 | measured 1.8 s (effort low) | no published comparison; successor of Sonnet 5 (§2d) |
| Claude Opus 5.5 (released 2026-09-22) | 4.00 | 0.20 | 20.00 | measured 3.4 s, max 13.8 s (effort low) | no published comparison; successor of Opus 5 (§2d) |
| Claude Fable 5.1 | 10.00 | 0.25 | 50.00 | not measured | −11.5 on a 200-item mixed set; 6/7 vs 7/7 writing defects |
| Gemini 3.8 Flash (Google; doubles 2027-01-01) | 0.75 | 0.075 | 3.75 | ~1.5 s (independent) | −1 to −4 on PubMedQA, Banking77, Portuguese legal fields |
| Grok 4.7 (xAI, released 2026-09-21) | 2.00 | 0.50 | 6.00 | measured 2.7 s (reasoning low) | no published comparison; successor of Grok 4.6 (§2d) |
| Kimi K3 (Moonshot) | 3.00 | 0.30 | 15.00 | not measured | −2 on a 200-item mixed set (n.s.) |
| DeepSeek V4 Pro (off-peak / peak) | 0.66 / 1.32 | 0.022 / 0.044 | 1.98 / 3.96 | not measured | no published comparison |

"Measured" = 10 short news-topic classifications per model through OpenRouter
with structured output, 2026-10-01; a rough figure, not a load test.
Gemini 3.8 Pro was not listed by Google or OpenRouter on 2026-09-22, nor on
OpenRouter on 2026-10-01; the Pro tier available was Gemini 3.1 Pro Preview at
2.00 / 0.20 / 12.00.

## 2c. Other decision models (same request body as Jev, checked 2026-10-19)

Jev stopped being the only model of its kind ten days after launch. By
2026-10-16 OpenRouter listed 27 decision-model entries (models, aliases and
tiers), among them OpenAI's own. Hugging Face holds more open-weight ones, and
JevBench's board of 2026-10-18 lists 258 systems.

OpenRouter's `/api/alpha/decisions` endpoint serves several vendors' decision
models with the same body (`state`, typed `questions`, `criteria`) and the same
answer shapes. Several open-weight models serve `POST /v1/systemone` too.
Switching between them, or keeping one as a fallback, is a change of the
`model` string or the URL. `scripts/probe.py` pilots any of them on the same
spec (`--model`, `--url`).

**Where to compare them.**
- **Rankings across many systems:** JevBench (https://benchmarkheaven.com/jev-models
  and `/jev-models/api`). It is updated almost daily. It covers calibration,
  latency and cost, and it includes the large open models.
- **Robustness on in-scope classification, Polish text and traps:** this
  skill's frozen benchmark. A per-model summary and how to read both sources
  are in the evidence reference, §5d.

The table below holds what a leaderboard does not: price, contract limits,
hosting, and one word on that benchmark's stress test, where a tie means
p > 0.05 against Jev 1.13.

| Model (id, listed) | $/M in | Context | Limits and contract | Hosting and extras | Stress test vs Jev |
|---|---|---|---|---|---|
| **Jev 1.13** (`typesafe/jev-1.13`, 09-18) | 0.042 | 32k on OR, 64k direct | Choice ≤ 255 options | US only; TypeSafe API, OpenRouter, Vercel, Cloudflare | reference |
| **Jev 1.14** (`typesafe/jev-1.14`, 10-14) | 0.042 | 262k on OR | as 1.13; adds Box questions (images, prototype only) | as 1.13; `jev-preview` points here, `jev-latest` still to 1.13 | tie (equal to 1.13; tighter p95) |
| **Liquid D1** (`liquid/d1`, 10-01) | 0.04 | 64k | none hit | – | behind (Polish traps, reviews) |
| **Liquid D1 Ultra** (`liquid/d1-ultra`, 10-15) | 0.042 | 32k | none hit | about a third of Jev's cost per decision | **tie**; under-confident on star scores |
| **OpenAI Decisions** (`openai/gpt-6-luna-decisions`, 10-06; public beta) | 0.10, input only | 1.05M | native contract differs (below); 1 refusal in 2,132 questions | text and images; ZDR, HIPAA, processing in the EU | **tie**; 1.2x Jev per English decision, 2.8x per Polish |
| **Perplexity Decider 27B** (`perplexity/pplx-decider-v1.1-27b`, 10-07) | 0.02 | not listed | none hit | about a fifth of Jev's cost; slower (p50 602 ms) | **tie**; strongest on Polish traps |
| **Perplexity Decider 1.2** (`perplexity/pplx-decider-v1.2`, 10-16) | 0.02 | 262k | none hit | the `pplx-decider-latest` alias points here | behind; worse than v1.1 |
| **Perplexity Decider Flash 1.2** (`perplexity/pplx-decider-flash-v1.2`, 10-16) | 0.01 | 262k | none hit | cheapest per decision of the set | behind; weak on star scores |
| **Mercury Decide** (`inception/mercury-decide:free`, 09-30) | free (preview) | 32k | 1,000 free requests a day per key | – | behind (Polish traps) |
| **Mercury Decide (paid)** (`inception/mercury-decide`, 09-30) | 0.02 | 32k | none hit | same model as the free preview | behind (Polish traps) |
| **Microsoft Decision-1** (`microsoft/microsoft-decision-1`, 10-09) | 0.042 | 32k | none hit | also on Azure Foundry | behind (sarcasm, injections) |
| **Cloudflare Clef** (`cloudflare/clef`, 10-01) | 0.24 | not listed | none hit | served by PrimeIntellect; looks trained on Banking77 | behind |
| **Cloudflare Clef Flash** (`cloudflare/clef-flash`, 10-01) | 0.021 | not listed | none hit | – | behind |
| **Cloudflare Clef Omni** (`cloudflare/clef-omni`, 10-09) | 0.15 | 65k | none hit | twice Jev's cost per decision | behind |
| **Span-01** (`respan/span-01`, 09-26; Lite tier free) | 0.02 | – | **Noul only**; state must be a string or a conversation | built to score behaviour in conversations | behind on yes/no reading |
| **Span-02** (`respan/span-02`, 10-16) | 0.01 | 131k | Choice, Score and Noul | p95 1.4 s | probably a tie (p = 0.06) |
| **Nace Drex 1.5** (`nace-ai/drex-v1.5`, 10-09) | 0.04 | 131k | none hit | – | far behind |
| **Nace Drex 2.0** (`nace-ai/drex-v2.0`, 10-12) | 0.06 | 131k | none hit | – | behind |
| **ScaleDown Classify-1** (`scaledown/classify-1`, 10-13) | 0.04 | 1M | **state must be a string or a text/document object** | 67 % uptime on OR; p95 2.7 s | behind |
| **Solar Decide** (`upstage/solar-decide`, 09-28) | 0.05 | 524k | **Choice ≤ 26 options** | p95 12.5 s | behind; overconfident |
| **Solar Decide Flash** (`upstage/solar-decide-flash`, 10-08) | 0.05 | not listed | **Choice ≤ 26 options** | – | far behind |
| **Tev1 4B experimental** (`togethercomputer/tev1-4b-experimental`, 09-30) | 0.042 | 32k | **Choice 2–20 options** | – | behind |
| **Kev 4B** (`jaredpalmer/kev-4b`, 09-25) | 0.042 | **8k** | none hit | open weights (LoRA on Qwen3.5-4B) | behind; under-confident |
| **H2O-Lightning-4B** (`h2oai/h2o-lightning-4b` v1.1, Hugging Face) | free to run | 40k; 4k on a 12 GB card | Choice ≤ 255 options; needs vLLM 0.30.0 and the vendor's shim | self-hosted, Apache-2.0, 9.3 GB in bf16 | behind; well calibrated |
| **Strands Decider 2B** (`StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`, Hugging Face) | free to run | not stated | serves `/v1/systemone` | self-hosted, Apache-2.0; trained on public sets | far behind |
| **basal-2.0 4.5B** (`Remek/basal-2.0-4.5B`, Hugging Face, 10-12; Bielik base) | free to run | 32k (4k as served here) | Choice ≤ 255 options; also `multi`, `act` with a certified error target, `tool`; needs the vendor's basal engine (GGUF on llama.cpp or Ollama with basal-serve in front) | self-hosted, Apache-2.0, Polish and English; 5 GB as GGUF Q8_0; the bf16 engine's start-up did not finish on a 12 GB card | behind; 85 % of Polish tickets fully right; very cautious confidence |
| **basal-2.0-mini** (`Remek/basal-2.0-mini`, Hugging Face, 10-12) | free to run | 32k | as basal-2.0 4.5B | self-hosted, 1.5B, 1.7 GB as GGUF Q8_0 | far behind |
What this means for a verdict:

- **Whenever Jev fits, price and pilot one or two rivals next to it.** Four
  decision models tied Jev on the stress test as well: Jev 1.14, Liquid D1
  Ultra, OpenAI Decisions and Perplexity Decider 27B (v1.1). Pick the second
  arm by what the team needs:
  - price: Perplexity v1.1 or D1 Ultra;
  - images, EU processing or HIPAA: OpenAI;
  - an existing vendor relationship: Azure, Cloudflare.

  Run the same spec on both arms (`probe.py --model`) and keep the loser as
  the fallback.
- **For a model newer than 2026-10-19, check JevBench first**, then pilot.
  Its Intelligence axis rewards reasoning. For a classification job, weigh
  its Calibration, Speed and Cost columns and your own pilot more than its
  headline score.
- **Pin versions.** Perplexity's 1.2 is worse than the v1.1 it replaced, and
  its `latest` alias already moved. Jev's `jev-preview` points to 1.14, which
  measured the same as 1.13, and `jev-latest` will follow.
- **Option counts and state types decide some cases outright.**
  - Tev1 rejects Choice questions with more than 20 options, and Solar with
    more than 26. Split the question hierarchically, or use another model.
  - ScaleDown and Span-01 refuse JSON object states.
- **Self-hosting is a real option, with a price in accuracy or hardware.**
  - On a 12 GB card the best measured here is H2O-Lightning-4B (at a 4k
    context), still behind Jev on traps. The Polish-trained basal-2.0 4.5B
    (GGUF Q8_0 on llama.cpp) was behind both on traps overall, ahead of H2O
    on star scores, and level with it on Polish tickets (85 % against 84 %).
  - The 26–31B open models need a 40–80 GB GPU: Quyet-1.0-Large, deck-31B,
    Surogate Rune and basal-omni-1.0-ultra. JevBench measured them and ranks
    some above Jev; this skill did not test them.
- **Thresholds never carry across models.** Kev and D1 Ultra are
  under-confident on some tasks and Solar is overconfident. A fallback model
  needs its own tuned thresholds.
- **Adversarial or sarcastic input narrows the field.**
  - Injected instructions, English and Polish (correct / items):
    - Jev and D1 Ultra: 10/10 and 14/15;
    - Perplexity v1.1 and GPT-6 Luna: 9/10 and 15/15;
    - OpenAI Decisions: 9/10 and 12/15;
    - Mercury: 10/10 and 11/15;
    - Microsoft: 8/10 and 10/15;
    - Perplexity 1.2: 6/10 and 9/15;
    - Solar: 7/10 and 8/15.
  - Sarcastic reviews: Jev and D1 Ultra 20/20, Microsoft 16/20, GPT-6 Luna
    and H2O 15/20.

  Small samples: they support "resists simple injections", never "safe as
  the only gate". For user-submitted content, pilot on hostile samples
  whatever the model.
- **OpenAI's Decisions API** (public beta on 2026-10-09) has its own native
  contract: `POST /v1/decisions` with `input` (text or images) and named
  `questions` of type `predicate` (a probability), `choice` or `score`. Only
  `gpt-6-luna` is available. A question can come back as a `refusal`, which
  OpenRouter surfaces as HTTP 502, so handle it. OpenAI claims about 10x the
  speed of its Responses API. Through OpenRouter's wrapper it was 2.8x faster
  than GPT-6 Luna through chat completions, and not faster than Jev.

## 2d. Superseded models (kept because measurements used them)

Each has a direct successor from the same vendor. They stay here, and in the
script's presets as tier "superseded", because published comparisons with
Jev were run on them. Quote their gap to Jev; price the successor.

| Model | $/M in | $/M out | Latency | Successor | Measured against Jev |
|---|---|---|---|---|---|
| GPT-5.6 Luna | 0.20 | 1.20 | 15 s default, ~1 s low | GPT-6 Luna (§2) | JevBench 97.1 % vs Jev 96.3 %; strongest cheap model of September |
| GPT-5.6 Sol (promo price "at least through 2026-11-21"; OpenRouter's OpenAI endpoint showed 2.00 / 10.00 on 2026-10-01) | 4.00 | 20.00 | ~3 s | GPT-6 Sol (§2b) | −6 overall on vendor workflows, −17 on invoices |
| Claude Sonnet 5 (still served) | 2.00 | 10.00 | ~2.2 s | Claude Sonnet 5.5 (§2b) | tie on vendor workflows and claim-support; −4 on synthetic tickets (n=100, noise) |
| Claude Opus 5 (still served) | 5.00 | 25.00 | ~3.4 s | Claude Opus 5.5 (§2b) | −5 on vendor workflows; +2 on fuzzy commit messages (n=800) |
| Grok 4.6 (xAI) | 2.00 | 6.00 | ~4.3 s | Grok 4.7 (§2b) | tie on synthetic tickets (n=100) |
| DeepSeek V4 Flash (legacy, third-party hosts only) | 0.055 | 0.11 | 1.6 s | DeepSeek V4.1 Flash (§2) | first-party API retired; no Jev comparison |

## 3. Rerankers and classification services

| Service | Price | Notes |
|---|---|---|
| Voyage rerank-2.5 / 3 (lite) | $0.05 ($0.02 lite) per M tokens, query tokens counted per document | 100 docs × 300 tokens ≈ $0.0017 per call |
| Jina reranker v3 / v3.5 | ~$0.05 per M tokens (secondary source; official page 404) | Open weights (0.6B); 100 docs × 256 tokens ≈ 100 ms |
| Cohere Rerank 4 Fast / Pro | ~$2.00 / $2.50 per 1k searches (secondary) | Jev tied Rerank 4 Pro on nDCG@10 in one 8-dataset test at ~1/5 the cost |
| Mistral Classifier API 3B / 8B | $0.10 / $0.04 per M tokens in and out | Purpose-built classification endpoint; Mistral Moderation is free |
| gpt-oss-safeguard-20b, Nemotron content-safety | $0.075–0.20 per M tokens | Open safety classifiers for guardrail use cases |
| Katanemo Arch-Router 1.5B | Self-host; vendor estimate $0.0013 per query on an L40S | 50 ms median; routing only |
| Fastino TLMs, Cleanlab TLM | Pricing not published | Subscription / quote |

When the task is "order these candidates by relevance", a dedicated reranker
is the default comparison, not an LLM. Jev competes on price and latency with
them and adds a probability per item; a reranker wins when lists are long
(hundreds of documents per query) because it scores all of them in one call.

## 4. Self-hosted encoder (DeBERTa / ModernBERT / SetFit)

- Throughput: ModernBERT-base ~76k tokens/s on an RTX 4090 (paper); a
  DeBERTa-v3-large "Jev-shaped" open model does ~518 questions/s on an H100.
  SetFit/MiniLM on CPU with ONNX: 0.3 ms per sample at batch 128.
- Hardware: RunPod RTX 4090 $0.34–0.74/h, L4 $0.44–0.49/h; HF Endpoints L4
  $0.70–0.80/h, T4 $0.50/h, CPU $0.033–0.27/h.
- Derived: at saturation an encoder costs roughly $0.6–1.4 per million
  512-token classifications on a 4090, i.e. $0.001–0.003 per million tokens,
  15–40x below Jev. But an always-on L4 is ~$320–580 per month whether or not
  traffic arrives; break-even against Jev is on the order of 10 billion input
  tokens per month for a single always-on GPU. Below that, Jev's zero
  infrastructure wins on cost; above it, or when data must stay in-house, the
  encoder wins.
- You pay in labels and maintenance: a fine-tune needs hundreds to thousands
  of labelled examples per task (one estimate: Jev zero-shot ≈ a BERT trained
  on ~230 labels for AG News/Banking77, on 2k+ for SST-2/TweetEval). Hosted
  SFT runs $0.34–1.00 per million training tokens (Together, Fireworks).
- Open "Jev-like" projects exist (Laya on ModernBERT-large, Kotoba's
  open-jev on DeBERTa-v3-large, openjev-sglang on Qwen3.6-35B) and land
  within 1–4 points of Jev on community benchmarks; none has Jev's breadth of
  evidence yet. They are the answer to "we need this on-prem".

## 5. Decision rules

- **Regex or rules pass the bar** → no model. Jev's job is meaning, not
  matching.
- **Thousands of labels exist and a trained model meets the bar** → keep it;
  revisit Jev when labels drift or new categories appear.
- **Few labels, semantic judgment, sub-second, probabilities used** → Jev, then
  pilot, with a rival that tied it as the second arm on the same spec (§2c);
  pick on your own data, and keep the loser as the fallback.
- **"Use Jev as the model behind our coding agent or chatbot"** → no; Jev
  generates nothing, and TypeSafe's `/introduction/coding-agents` page says
  so. If the
  real question is which LLM each request should go to, that is routing:
  price Jev Router or a self-built Choice over models against a fixed model.
- **Judgment needs a little generation or long messy inputs** → cheap-tier LLM
  with structured output at low reasoning; consider Jev as a pre-filter or
  verifier in front of it.
- **The bar is frontier accuracy on long or multi-field judgments** → do not
  expect Jev alone to reach it; propose the cascade (Jev with a confidence
  gate at 0.8–0.9, frontier model for the rest) and price both arms.
- **Long lists to rerank** → dedicated reranker or a cheap-tier LLM; Jev only
  for short shortlists (≤ 30) or with code pre-filtering.
- **On-prem, EU residency, or >10B tokens/month** → self-hosted encoder or an
  open decision model (§2c; JevBench's open-weights board), or OpenAI
  Decisions for EU processing.
- **Extraction of open values** → LLM extracts, Jev verifies per field or
  selects among regex candidates.
