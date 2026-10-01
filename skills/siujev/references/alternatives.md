# Alternatives: what else does the job, and when it wins

Compare Jev against two tiers, for two different reasons. For **cost**, the
honest rival is the cheap "flash" tier (GLM-5.3-Flash, Qwen3.8-Flash, DeepSeek
V4.1 Flash, Gemini Flash-Lite, GPT-6 Luna or GPT-5.6 Luna at low reasoning,
Claude Haiku 4.5): on short bounded decisions Jev's accuracy sits in that band
or above it, and its cost advantage there is 3–15x per decision, not the
vendor's 400x. For the **accuracy ceiling**, show the frontier tier (GPT-5.6
Terra / Sol, GPT-6 Sol / 6.1 Sol / Astra, Claude Sonnet 5.5 / Opus 5.5 / Fable
5.1, Gemini 3.8 Flash). The measured comparisons below were run on the models
current in mid-September (Terra, Sonnet 5, Opus 5, Sol, Astra, Fable 5.1);
their successors released 2026-09-22 to 09-29 (GPT-6 Luna, GPT-6 Sol, GPT-6.1
Sol, Claude Opus 5.5, Claude Sonnet 5.5, Grok 4.7) appear in no comparison
cited in `evidence.md`, so quote the gap measured against the predecessor
and plan as if it is at least as large. On short crisp
tasks Jev ties Terra and Sonnet 5 (−2 to +1 points; it beat Terra 89 vs 88 on
100k AG News rows), trails Terra by 5–7 points on 77-way overlapping intents,
and trails Sol / Opus 5 / Astra / Fable 5.1 by 6–12 points on long, fuzzy,
multi-field documents (17 on invoices in the vendor's own eval). A
confidence-gated cascade (Jev first, frontier model for the uncertain 20–37 %)
lands within 1–2 points of the frontier model at 26–37 % of its cost. The
table in `evidence.md` has every comparison with its n and source. Also
compare against a self-hosted encoder and against plain code. Prices below were checked
2026-09-21 and re-checked 2026-10-01 on vendor pages and OpenRouter; they move
monthly, so re-check the source before quoting. "OR p50" is OpenRouter's median
latency over a 30-minute window on 2026-09-21, a rough indicator only; models
added on 2026-10-01 have no latency figure yet. OpenAI's pricing page lists
service tiers: Batch and Flex at 50 % of the standard price, Fast at 2x, and
Ultrafast at 6x (GPT-6 Astra only); the tables show standard prices.

## 1. The option ladder

Work down this ladder and stop at the first rung that meets the bar.

| Rung | When it wins | Cost order | Latency |
|---|---|---|---|
| **Plain code** (regex, parser, lookup, rules) | The condition is lexical or structural and stable; you can enumerate it | ~0 | µs |
| **Existing trained classifier** (TF-IDF+LR, DeBERTa, SetFit) | You already have thousands of labels and a model that meets the bar; a spam test showed Jev zero-shot 98.3 % vs TF-IDF+LR on 14.8k labels 98.4 % | GPU/CPU rent, idle cost | 1–40 ms |
| **Jev** | Judgment needs meaning, not lexical match; labels are few or shifting; you want calibrated probabilities and sub-second latency without training | $0.042/M input, output free | 100–500 ms (independent p50 240–385 ms) |
| **Cheap LLM with structured output** | Same as Jev but you also need short generation, longer or messier inputs, or tasks where Jev measurably trails (long fuzzy single-shot judgments, 77-way intents) | $0.03–0.30/M in, $0.13–1.20/M out | 0.4–2 s (up to 5–15 s if reasoning is on by default) |
| **Frontier LLM** | Multi-step reasoning, generation, or the extra accuracy pays for itself (invoice-type extraction: vendor eval 79 % vs Jev 62 %) | $1–10/M in, $5–50/M out | 2–40 s |
| **Human** | Stakes or ambiguity exceed any model; use Jev to shrink the queue, not to empty it | $ per item | minutes to days |

## 2. Cheap LLMs in Jev's tier (prices per million tokens, checked 2026-09-21, re-checked 2026-10-01)

| Model | $/M in | $/M out | OR p50 latency | Notes |
|---|---|---|---|---|
| Qwen3.7 Flash (Alibaba, ≤32k input) | 0.03 | 0.13 | 738 ms | Cheapest hosted rival; beat Jev on cost in one independent test, lost on accuracy in that test (82–95 % vs 95–100 %) |
| Amazon Nova Micro | 0.035 | 0.14 | 376 ms | Fast and cheap, weak model, text only |
| Mistral Nemo 12B (DeepInfra) | 0.019 | 0.03 | 475 ms | 2024 model, weak; open weights |
| Qwen3-30B-A3B (open, cheapest host) | 0.048 | 0.19 | ~1.1 s | Self-host candidate |
| GPT-5 nano | 0.05 | 0.40 | 1.3 s | Reasoning on by default |
| DeepSeek V4 Flash (legacy, 3rd-party hosts) | 0.055 | 0.11 | 1.6 s | First-party API retired |
| GPT-6 Luna (OpenAI, released 2026-09-22) | 0.10 | 0.50 | not measured yet | Cheaper than GPT-5.6 Luna (0.20 / 1.20); OpenRouter's description names classification among its target workloads; Flex 0.05 / 0.25. No Jev comparison yet, so include it in a pilot when OpenAI is an option |
| Gemini 2.5 Flash-Lite | 0.10 | 0.40 | 386 ms | Highest-volume cheap model on OpenRouter; native JSON schema |
| Ministral 3B / 8B | 0.10 / 0.15 | 0.10 / 0.15 | 304 / 346 ms | Latency peers of Jev; Mistral also sells a Classifier API (8B) at 0.04 / 0.04 |
| ByteDance Seed 2.0-mini | 0.10 | 0.40 | 371 ms | Fastest Chinese model measured |
| Qwen3.8 Flash | 0.15 | 0.47 | 5.0 s default, ~0.7 s with reasoning low | DevX ticket routing 90 % |
| GLM-5.3 Flash (Z.ai) | 0.15 (0.075 on DeepInfra) | 0.50 | 3.2 s default, ~0.9 s low | DevX 94–95 %, best of the sub-$0.20 tier on the AA index |
| DeepSeek V4.1 Flash (first-party) | 0.15 off-peak / 0.30 peak | 0.60 / 1.20 | 2.9 s default, ~1.7 s low | DevX 97 % (statistical tie with Jev at n=100); cache hits ~0.003. Some of the ~30 third-party hosts on OpenRouter charge as little as 0.03 / 0.50, on par with Jev's input price; check the host's quantisation and latency before treating that as the rival price |
| Mistral Small 4 | 0.15 | 0.60 | 416 ms | Measurably worse than Jev in two tests (79–86 %) |
| StepFun 3.7 Flash | 0.16–0.20 | 0.92–1.15 | 362 ms | Fast |
| GPT-5.6 Luna | 0.20 | 1.20 | 15 s default, ~1 s low | JevBench 97.1 % vs Jev 96.3 %; strongest of the cheap tier |
| Gemini 3.1 / 3.5 Flash-Lite | 0.25 / 0.30 | 1.50 / 2.50 | 0.5 / 1.2 s | 3.5 had the worst calibration in the Supa test (ECE up to 0.16) |
| MiniMax M2.7 / M3 | 0.30 | 1.20 | ~1.7 s | |
| Kimi K2.6 | 0.95 (0.41 via Baidu on OR) | 4.00 | 1.1 s | Not cheap at first-party price; K2.5 retired 2026-08-31 |
| Claude Haiku 4.5 | 1.00 | 5.00 | 0.8 s | Beat Jev on single-question phishing (81 vs 63 %); 12–27x Jev's cost |

Per-decision arithmetic that matters more than the per-token price:

- A Jev request bills the state once plus ~30–50 tokens per question; an LLM
  prompt carries instructions plus the content and pays for output tokens. In
  independent tests Jev used 85 tokens where the LLM prompt used 910 for the
  same decision, so Jev's per-decision advantage over a same-tier LLM is
  usually 3–15x, not the vendor's 400x. Against Qwen3.7 Flash it can be a loss.
- Reasoning-default models (DeepSeek, GLM, Qwen 3.8, GPT-5.6) must be run with
  reasoning at its lowest setting for classification; otherwise cost triples
  and latency reaches 3–15 s.
- Batch tiers (OpenAI, Google, Mistral) halve LLM prices for offline jobs;
  Jev has no batch discount but also no output charge.
- Jev's 32k state ceiling forces one request per passage when reranking long
  lists; in a 100-chunk RAG rerank the cheap flash LLMs did slightly better at
  a similar cost and Jev lost its latency edge (6.8 s per question for 100
  calls). Rerank short lists, or pre-filter in code.

## 2b. Frontier tier (prices per million tokens, checked 2026-09-22, re-checked 2026-10-01)

| Model | $/M in | $/M cached in | $/M out | Where Jev stands |
|---|---|---|---|---|
| GPT-5.6 Terra (OpenAI) | 2.00 | 0.20 | 12.00 | tie on short crisp tasks; −5–7 on 77-way intents |
| GPT-5.6 Sol (OpenAI, promo "at least through 2026-11-21") | 4.00 | 0.40 | 20.00 | −6 overall on vendor workflows, −17 on invoices |
| GPT-6 Sol (OpenAI, released 2026-09-22) | 2.00 | 0.20 | 10.00 | no published comparison; successor tier to 5.6 Sol at half its price |
| GPT-6.1 Sol (OpenAI, released 2026-09-29) | 2.00 | 0.10 | 10.00 | no published comparison |
| GPT-6 Astra (OpenAI) | 10.00 | 1.00 | 50.00 | −6.5 on a 200-item mixed set |
| Claude Sonnet 5.5 (released 2026-09-28) | 2.00 | 0.20 | 10.00 | no published comparison; same price as Sonnet 5 |
| Claude Sonnet 5 (still served) | 2.00 | 0.20 | 10.00 | tie on vendor workflows and claim-support; −4 on synthetic tickets (n=100, noise) |
| Claude Opus 5.5 (released 2026-09-22) | 4.00 | 0.20 | 20.00 | no published comparison; 20 % cheaper than Opus 5 |
| Claude Opus 5 (still served) | 5.00 | 0.50 | 25.00 | −5 on vendor workflows; +2 on fuzzy commit messages (n=800) |
| Claude Fable 5.1 | 10.00 | 0.25 | 50.00 | −11.5 on a 200-item mixed set; 6/7 vs 7/7 writing defects |
| Gemini 3.8 Flash (Google; doubles 2027-01-01) | 0.75 | 0.075 | 3.75 | −1 to −4 on PubMedQA, Banking77, Portuguese legal fields |
| Grok 4.7 (xAI, released 2026-09-21) | 2.00 | 0.50 | 6.00 | no published comparison; same price as Grok 4.6 |
| Grok 4.6 (xAI) | 2.00 | 0.50 | 6.00 | tie on synthetic tickets (n=100) |
| Kimi K3 (Moonshot) | 3.00 | 0.30 | 15.00 | −2 on a 200-item mixed set (n.s.) |
| DeepSeek V4 Pro (off-peak / peak) | 0.66 / 1.32 | 0.022 / 0.044 | 1.98 / 3.96 | no published comparison |

Gemini 3.8 Pro was not listed by Google or OpenRouter on 2026-09-22, nor on
OpenRouter on 2026-10-01; the Pro tier available was Gemini 3.1 Pro Preview at
2.00 / 0.20 / 12.00.
OpenRouter's OpenAI endpoint for GPT-5.6 Sol showed 2.00 / 10.00 on
2026-10-01 while OpenAI's own page still said 4.00 / 20.00; quote OpenAI's
price for first-party use.

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
  pilot.
- **"Use Jev as the model behind our coding agent or chatbot"** → no; Jev
  generates nothing, and TypeSafe's `/introduction/coding-agents` page says
  so. If the
  real question is which LLM each request should go to, that is routing:
  price Jev Router or a self-built Choice over models against a fixed model.
- **Judgment needs a little generation or long messy inputs** → cheap LLM
  with structured output at low reasoning; consider Jev as a pre-filter or
  verifier in front of it.
- **The bar is frontier accuracy on long or multi-field judgments** → do not
  expect Jev alone to reach it; propose the cascade (Jev with a confidence
  gate at 0.8–0.9, frontier model for the rest) and price both arms.
- **Long lists to rerank** → dedicated reranker or a cheap flash LLM; Jev only
  for short shortlists (≤ 30) or with code pre-filtering.
- **On-prem, EU residency, or >10B tokens/month** → self-hosted encoder or an
  open Jev-like model.
- **Extraction of open values** → LLM extracts, Jev verifies per field or
  selects among regex candidates.
