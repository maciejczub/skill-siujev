# Decision-model benchmark: full record (2026-10-01 to 10-19)

This is the complete record of the decision-model benchmark that the siujev
skill ran between 2026-10-01 and 2026-10-19. It is kept for readers and for
reproducibility; it is **not** loaded by the skill. The skill keeps a short
summary (`skills/siujev/references/evidence.md` §5d) and points to
[JevBench](https://benchmarkheaven.com/jev-models) for current rankings.

**Status: frozen.** From 2026-10-19 the project no longer adds every new
decision model here. JevBench by Benchmark Heaven
([repository](https://github.com/fstandhartinger/jevbench)) measures far more
systems (258 on its board of 2026-10-18), on sealed items, with calibration,
speed and cost axes and a 23-language view. This benchmark measured something
narrower that JevBench does not: in-scope classification (intents, star
scores, yes/no reading), Polish business text, named traps (injections,
sarcasm, Polish return vs complaint, text without diacritics), fresh
unpublished mirrors as a contamination check, and paired McNemar tests
against Jev. New models are run here only when they are serious candidates
for that niche.

The harness, the item sets (unpublished, on purpose) and the raw runs live in
the maintainer's private research folder.

## Contents
- 1. First round: seven decision models and GPT-6 Luna (2026-10-01)
- 2. Failure-mode stress test (2026-10-02)
- 3. Six more models, including OpenAI's (2026-10-09)
- 4. Microsoft Decision-1 and two self-hosted models (2026-10-17)
- 5. Jev 1.14 and eight more models (2026-10-17)
- 6. basal-2.0, self-hosted Polish models (2026-10-19)

## 1. First round: seven decision models and GPT-6 Luna (2026-10-01)

Run by the skill's author through OpenRouter's `/api/alpha/decisions`
endpoint. Every decision model got the identical request body (state,
questions, criteria). GPT-6 Luna, as a cheap-LLM reference, got one
chat-completions call per item with the same questions as a strict JSON
schema and reasoning set to `none`. Each model ran with 4 concurrent
workers, all models in parallel, from one client in Poland; latency
includes OpenRouter overhead. About 14,000 requests in total cost $0.77.
Mercury Decide's fresh-set run followed on 2026-10-02, once its free daily
quota had reset.

Two kinds of data:

- **Public sets** (seeded samples, n = 200 each): AG News (Choice, 4),
  Banking77 (Choice, 77), Yelp stars (Score, 5) and BoolQ (Noul), plus the
  48 Polish listings from the skill's evidence §5b, run 3 times each.
- **Fresh mirrors**, written for this test on 2026-10-01 and deliberately
  **never published**, so no model can have trained on them (686 items):
  - news on invented events
  - customer messages for the 77 Banking77 labels
  - a new 19-intent telecom taxonomy
  - reviews of invented businesses
  - yes/no questions over passages about invented subjects
  - 84 Polish support tickets: a team Choice plus refund and churn Nouls

  Gemini 3.8 Flash re-labelled every item blind. It disagreed on 2 items, both
  get_physical_card vs order_physical_card, and those were dropped.

Accuracy, %:

| Model | AG News | Banking77 | Yelp exact | BoolQ | Polish Nouls / Choice | Fresh: news / B77 / telecom 19 / reviews / yes-no / PL team / PL Nouls |
|---|---|---|---|---|---|---|
| Jev 1.13 | 88.5 | 80.5 | 67.0 | 89.0 | 97.2 / 85.4 | 100 / 99.3 / 100 / 98 / 100 / 97.6 / 99.4 |
| Liquid D1 | 89.5 | 87.5 | 66.0 | 90.0 | 96.5 / 87.5 | 100 / 98.7 / 99.3 / 96 / 100 / 100 / 99.4 |
| Mercury Decide | 91.0 | 86.5 | 66.5 | 91.5 | 98.1 / 89.6 | 100 / 98.0 / 98.7 / 100 / 100 / 97.6 / 99.4 |
| Tev1 4B | 89.5 | max 20 options | 66.0 | 90.5 | 93.8 / 91.0 | 98 / – / 98 / 91 / 100 / 96.4 / 99.4 |
| Solar Decide | 89.0 | max 26 options | 61.0 | 85.5 | 94.4 / 86.8 | 100 / – / 98 / 87 / 96 / 94.0 / 94.6 |
| Kev 4B | 89.5 | 87.0 | 68.5 | 82.0 | 95.1 / 89.6 | 96 / 96.7 / 88.2 / 91 / 96 / 90.5 / 85.7 |
| Span-01 (Noul only) | – | – | – | 83.0 | 96.5 / – | – / – / – / – / 93 / – / 98.8 |
| GPT-6 Luna (LLM) | 88.0 | 81.5 | 61.0 | 86.5 | 97.9 / 93.8 | 100 / 100 / 100 / 90 / 99 / 97.6 / 99.4 |

- **How to read the differences.** With n = 200, Wilson intervals are about
  ±5 points, so most gaps in the table are noise. Paired McNemar tests on
  the same items found these differences against Jev at p < 0.05:
  - better than Jev on public Banking77: D1 (17 vs 3 discordant items),
    Mercury (18 vs 6) and Kev (20 vs 7)
  - worse than Jev on public BoolQ: Kev
  - worse than Jev on Yelp and on the fresh reviews: GPT-6 Luna
  - worse than Jev on the fresh reviews and fresh Polish tickets: Solar
  - worse than Jev on fresh telecom intents (18 vs 0) and fresh Polish
    tickets (21 vs 0): Kev
  - worse than Jev on the fresh yes/no questions: Span-01

  Everything else is a statistical tie.
- **The contamination check.** The 6–7-point lead that D1, Mercury and Kev
  had on public Banking77 did not survive fresh messages with the same 77
  labels:
  - fresh results: Jev 99.3, D1 98.7, Mercury 98.0, Kev 96.7
  - gain from public to fresh: Jev +18.8 and Luna +18.5, against Mercury
    +11.5, D1 +11.2 and Kev +9.7

  This is consistent with exposure to Banking77 or its label conventions
  during training, but it does not prove it. The fresh sets have clean
  author labels, so every model scored higher on them and the top models hit
  the ceiling, which compresses gaps. Kev's public strength did not carry
  over to new text in any fresh task. Mercury and D1 tied Jev on every
  fresh task (no paired difference at p < 0.05).
- **Calibration.** Expected calibration error (ECE) of the top answer on
  AG News, Banking77 and BoolQ:

  | Model | AG News | Banking77 | BoolQ |
  |---|---|---|---|
  | Liquid D1 | 0.04 | 0.05 | 0.03 |
  | Mercury Decide | 0.07 | 0.08 | 0.05 |
  | Jev 1.13 | 0.08 | 0.09 | 0.04 |
  | Solar Decide | 0.10 | – | 0.12 |

  - On the fresh sets Mercury is the best calibrated (ECE ≤ 0.04 on every
    task); Jev's ECE is ≤ 0.06.
  - Kev is strongly underconfident: on fresh telecom intents only 20 % of
    answers reach 0.8, although all of those are right. Thresholds do not
    transfer between models; tune them per model.
- **Latency, p50 / p95** (all requests):

  | Model | p50 | p95 |
  |---|---|---|
  | Jev | 341 ms | 458 ms |
  | Tev1 | 340 ms | 566 ms |
  | Mercury | 389 ms | 575 ms |
  | D1 | 424 ms | 992 ms |
  | Span | 605 ms | 1.2 s |
  | Kev | 619 ms | 901 ms |
  | Solar | 720 ms | **12.5 s** |
  | GPT-6 Luna | 1.2 s | 1.7 s |
- **Cost per 1,000 decisions** (AG News / Banking77):

  | Model | AG News | Banking77 |
  |---|---|---|
  | Mercury | free | free |
  | Kev | $0.005 | $0.035 |
  | D1 | $0.005 | $0.019 |
  | Jev | $0.018 | $0.071 |
  | Solar | $0.022 | – |
  | GPT-6 Luna | $0.026 | $0.177 |

  Providers count tokens differently for the same body. For the same AG News
  request Jev counted 423 input tokens, D1 131, Kev 121 and Solar 440. So
  compare cost per decision, never price per token.

Read this as one benchmark by one person: the fresh items were written by an
LLM (Claude) and verified by another (Gemini), which may favour models trained
on synthetic LLM text; short texts only; one client location; prices as of
the run date. It is enough to say "pilot D1 next to Jev"; it is not enough to
switch without your own data.

## 2. Failure-mode stress test (2026-10-02)

The fresh sets in section 1 were too easy to separate the top models, so a second
unpublished set was written, 500 items, each built around a named trap taken
from the documented weaknesses of decision models. Two verifiers from
different families (Gemini 3.8 Flash, DeepSeek V4 Pro) labelled every item
blind. Gemini agreed with every label except 2 adjacent star levels; DeepSeek
differed on 6 items, 3 of them because it followed an injected instruction.
No item was dropped. Same harness and question wording as section 1.

Accuracy, %:

| Model | Telecom intents (19), n=120 | Banking77 labels (77), n=80 | Passage yes/no, n=120 | Reviews, exact, n=80 | Polish tickets, all 3 labels right, n=100 | Pooled vs Jev: only Jev right / only model right |
|---|---|---|---|---|---|---|
| Jev 1.13 | 98.3 | 100 | 100 | 100 | 97 | reference |
| GPT-6 Luna (LLM) | 99.2 | 100 | 100 | 92.5 | 99 | 7 / 4, tie |
| Liquid D1 | 99.2 | 100 | 100 | 95.0 | 91 | 11 / 2, p = 0.02 |
| Mercury Decide | 100 | 98.8 | 99.2 | 97.5 | 89 | 15 / 5, p = 0.04 |
| Tev1 4B | 93.3 | max 20 options | 96.7 | 82.5 | 86 | 35 / 0 |
| Solar Decide | 95.0 | max 26 options | 92.5 | 81.2 | 70 | 56 / 1 |
| Kev 4B | 89.2 | 95.0 | 90.8 | 88.8 | 75 | 62 / 5 |
| Span-01 (Noul only) | – | – | 86.7 | – | 87 (two Nouls) | 29 / 3 |

Mercury ran its last 260 items on 2026-10-03, once its free daily quota had
reset.

What the traps showed (correct / items):

- **Jev was the most robust model on traps**, at or near the ceiling on
  every one. Its misses were 2 of 15 "other" messages full of telecom words,
  1 of 15 Polish injections, and 2 other Polish tickets. On the hard items it
  kept 90–100 % of answers above 0.8 confidence, and all of those were right
  (ECE 0.01–0.07).
- **Liquid D1 fell behind Jev once the items got hard**: pooled over the
  500 items it was right where Jev was wrong 2 times and wrong where Jev was
  right 11 times. The losses were Polish tickets (zwrot vs reklamacja 22/25
  against Jev's 24/25, injections 13/15) and reviews (95 vs 100 exact). On
  English intents and reading it still tied. **Mercury Decide** showed the
  same pattern (15 vs 5, p = 0.04), almost all of it on Polish tickets:
  zwrot vs reklamacja 19/25 and Polish injections 11/15, while it tied or led
  on the English sets.
- **Injected instructions** (text in the state that tells the classifier
  what to answer):

  | Model | English | Polish |
  |---|---|---|
  | Jev 1.13 | 10/10 | 14/15 |
  | Liquid D1 | 10/10 | 13/15 |
  | GPT-6 Luna | 9/10 | 15/15 |
  | Mercury Decide | 10/10 | 11/15 |
  | Kev 4B | 9/10 | 13/15 |
  | Tev1 4B | 8/10 | 13/15 |
  | Solar Decide | 7/10 | 8/15 |

  Small samples: this supports "resists simple injections", not "safe as
  the only gate".
- **Sarcastic reviews** were the hardest trap for everything but Jev, D1 and
  Mercury: Jev 20/20, D1 19/20, Mercury 19/20, GPT-6 Luna 15/20, Kev 13/20,
  Solar 13/20, Tev1 9/20.
- **Comparing two stated numbers or ordering two stated dates** in a short
  passage did not trip Jev, D1 or GPT-6 Luna (20/20 each on both traps;
  Mercury 39/40),
  although numbers and dates are documented Jev failure modes. The traps
  cover only a comparison of two values that the passage states; arithmetic,
  counting, date windows and long documents were not tested, so keep those
  in code. Span-01 (14/20 on dates), Solar and Tev1 (17/20) did slip.
- **Long passages with distractors** (about 300 words, several similar
  entities): Kev 17/24, Span-01 19/24, Solar 22/24; the rest 24/24.
- **Polish without diacritics, slang, typos**: Kev 7/15, Solar and Tev1
  11/15; Jev and GPT-6 Luna 15/15, D1 and Mercury 14/15.
- **Confidence is not comparable across models.** Solar answered 100 % of
  intent items above 0.8 and was right on 95 %; Kev cleared 0.8 on only 17 %
  and was right on all of those. A gate tuned for one model is wrong for
  another.

Same caveats as section 1: items written by one LLM family and verified by two
others, short texts, one run per item. "Hard" here means hard for small
decision models, not ambiguous: two frontier-class LLMs agreed with almost
every label, and Jev, D1 and GPT-6 Luna still score 91–100 %.

## 3. Six more models, including OpenAI's (2026-10-09)

Between 2026-10-01 and 10-09 OpenRouter listed more decision models, among
them OpenAI's own. Four were run through the whole harness of sections 1 and 2
(2,132 requests each: public sets, fresh mirrors and the 500-item stress
test, same questions, same labels, same day) against the earlier results:
OpenAI Decisions (`openai/gpt-6-luna-decisions`), Perplexity Decider 27B,
Cloudflare Clef and Cloudflare Clef Flash. They are reached through
OpenRouter's wrapper, which takes Jev's request body. For OpenAI that is not
the native `/v1/decisions` contract (`predicate`, `choice`, `score`), so
latency includes OpenRouter. The four runs cost about $0.24 in total.

Accuracy, %:

| Model | Public: AG News / Banking77 / BoolQ | Fresh: Banking77 labels / reviews exact | Stress test: intents / yes-no / reviews exact / Polish all-correct | Stress test, pooled vs Jev (only Jev right / only model right) |
|---|---|---|---|---|
| Jev 1.13 | 88.5 / 80.5 / 89.0 | 99.3 / 98.0 | 98.3 / 100 / 100 / 97 | reference |
| OpenAI Decisions | 88.0 / 79.4 / 88.0 | 97.4 / 97.0 | 99.2 / 100 / 97.5 / 96 | 5 / 3, p = 0.73 |
| Perplexity Decider 27B | 91.0 / 81.5 / 93.5 | 99.3 / 100 | 99.2 / 100 / 96.2 / 99 | 5 / 5, p = 1.0 |
| Cloudflare Clef | 92.0 / 94.0 / 88.5 | 95.4 / 93.0 | 97.5 / 100 / 96.2 / 90 | 13 / 0, p < 0.001 |
| Cloudflare Clef Flash | 90.5 / 95.0 / 88.0 | 96.1 / 96.0 | 95.0 / 97.5 / 95.0 / 86 | 26 / 1, p < 0.001 |

- **OpenAI Decisions tied Jev everywhere**, including the stress test. Its
  injection items: 9/10 in English, 12/15 in Polish. Its Polish return vs
  complaint was 25/25. It refused one of 2,132 questions (a Banking77
  message), which arrives as a `refusal` answer natively and as HTTP 502 on
  OpenRouter. On the same 2,132 requests it was not faster than Jev in this
  setup (p50 437 against 358 ms, p95 720 against 689 ms), though it was
  2.8x faster than GPT-6 Luna through chat completions (1,225 ms).
- **Perplexity Decider 27B also tied Jev**, was the strongest on Polish traps
  (99 % all three labels right, 15/15 Polish injections), and beat Jev on
  public BoolQ (93.5 against 89.0, p = 0.02). Its answers on reviews were
  less confident: only 68 % of stress-test reviews cleared 0.8, although all
  of those were right.
- **Clef and Clef Flash look trained on Banking77.** Public Banking77 94.0 and
  95.0 beat Jev's 80.5 (27 items only Clef had right, none only Jev), but on a
  fresh mirror with the same labels they scored 95.4 and 96.1 and trailed
  Jev's 99.3. From public to fresh they gained +1.4 and +1.1 points where Jev
  gained +18.8 and every other model at least +9.7. That fits training-data
  exposure but does not prove it. On the stress test both were significantly
  behind Jev, mostly on Polish tickets (Clef all-correct 90 %, Flash 86 %) and
  on "other" messages full of telecom words (12/15 and 11/15).
- **Cost per 1,000 AG News decisions** (input tokens counted by each
  provider):

  | Model | Tokens | Cost | Banking77 / Polish tickets |
  |---|---|---|---|
  | Perplexity Decider 27B | 189 | $0.0038 | $0.019 / $0.015 |
  | Clef Flash | 245 | $0.0062 | $0.046 / $0.016 |
  | Clef | 245 | $0.0115 | $0.090 / $0.033 |
  | Jev 1.13 | 423 | $0.0178 | $0.071 / $0.031 |
  | OpenAI Decisions | 209 | $0.0209 | $0.099 / $0.088 |

  OpenAI's per-token price is 2.4x Jev's but it counts fewer tokens on
  English, so it costs only 1.2x Jev per English decision; Polish text counts
  as 876 tokens against Jev's 736, which makes it 2.8x.
- **Latency, p50 / p95:** OpenAI 437 / 720 ms, Clef Flash 534 / 1,564 ms,
  Clef 569 / 1,379 ms, Perplexity 602 / 1,068 ms; Jev 358 / 689 ms on the
  same requests.

The same day two more listed models ran through the same harness:

| Model | Public: AG News / BoolQ | Fresh: reviews exact / yes-no | Stress test: intents / yes-no / reviews exact / Polish all-correct | Pooled vs Jev |
|---|---|---|---|---|
| Mercury Decide (paid tier) | 91.0 / 90.5 | 100 / 100 | 100 / 99.2 / 97.5 / 88 | 16 / 5, p = 0.03 |
| Solar Decide Flash | 86.5 / 82.5 | 74.0 / 89.0 | 91.7 / 81.7 / 78.8 / 51 | 93 / 0, p < 0.001 |

- **The paid Mercury tier is the free preview's twin**: same accuracy on every
  set, same weakness (Polish return-vs-complaint 19/25 and injections 12/15),
  and a price: $0.02 per million input tokens, $0.0036 per 1,000 AG News
  decisions (about a fifth of Jev), p50 476 / p95 915 ms. The free preview
  stays capped at 1,000 requests a day per key. Its Polish tickets are
  billed as 163 tokens against 544 on the free tier for the same requests,
  so compare cost per decision, not token counts.
- **Solar Decide Flash is far behind its sibling and Jev**: stress-test
  Polish tickets 51 % all-correct and 6/15 Polish injections, sarcastic
  reviews 12/20, public star scoring 56.5 %. It accepts at most 26 Choice
  options (77-way Banking77 failed with HTTP 422 on all 432 requests that
  used it) and is poorly calibrated on star scoring (ECE 0.30 on public
  reviews: of the 71 % of answers above 0.8, only 65 % were right).
  Slowest of the set: p50 905 / p95 1,646 ms.

Same caveats as sections 1 and 2.

## 4. Microsoft Decision-1 and two self-hosted models (2026-10-17)

Run through the same 2,132-request harness as sections 1 to 3: Microsoft Decision-1
(`microsoft/microsoft-decision-1` on OpenRouter) and two open-weight models
served locally in Docker on one RTX 4070 (12 GB): Strands Decider 2B and
H2O-Lightning-4B. The local servers speak the same `/v1/systemone` body.
Latency of the local ones is on that GPU without network, so it is not
comparable with the API rows.

Accuracy, %:

| Model | Public: AG News / Banking77 / BoolQ | Fresh: Banking77 labels / reviews exact | Stress test: intents / yes-no / reviews exact / Polish all-correct | Stress test, pooled vs Jev (only Jev right / only model right) |
|---|---|---|---|---|
| Jev 1.13 | 88.5 / 80.5 / 89.0 | 99.3 / 98.0 | 98.3 / 100 / 100 / 97 | reference |
| Microsoft Decision-1 | 88.0 / 88.5 / 85.5 | 99.3 / 93.0 | 97.5 / 98.3 / 90.0 / 88 | 25 / 5, p < 0.001 |
| H2O-Lightning-4B (bf16, two-way) | 88.0 / 91.0 / 86.0 | 98.7 / 89.0 | 97.5 / 98.3 / 87.5 / 84 | 27 / 1, p < 0.001 |
| Strands Decider 2B | 88.0 / 86.0 / 78.5 | 92.8 / 80.0 | 91.7 / 78.3 / 65.0 / 62 | 105 / 1, p < 0.001 |

- **None of the three matched Jev once the items got hard.** Even so,
  H2O-Lightning-4B and Microsoft Decision-1 are close on English intents
  (97.5 vs 98.3) and on Banking77-style labels (100 vs 100).
- **Where they lose** (correct / items): sarcastic reviews, Jev 20/20 against
  Microsoft 16/20, H2O 15/20 and Strands 3/20; Polish return-vs-complaint,
  Jev 24/25 against Microsoft 21/25, H2O 19/25 and Strands 13/25; Polish
  injected instructions, Jev 14/15 against Microsoft 10/15 and H2O 14/15.
  Microsoft followed 2 of 10 English injections.
- **The public Banking77 lead is again a mirage.** Microsoft (88.5), H2O (91.0)
  and Strands (86.0) beat Jev's 80.5 on the public set, then gained only +10.8,
  +7.7 and +6.8 points on a fresh mirror against Jev's +18.8. Strands' model
  card lists Banking77 among its training datasets; for the other two the
  cause is unknown.
- **Calibration.** H2O is well calibrated on short items (ECE 0.03 to 0.06 on
  intents) and gates cleanly on yes/no questions. Strands never reached 0.8
  confidence on star scores (ECE 0.40 on fresh reviews). Microsoft kept only
  76 % of fresh reviews above 0.8.
- **Cost and speed.** Microsoft Decision-1 is $0.042 per million input
  tokens: $0.0054 per 1,000 AG News decisions (counts 128 tokens against Jev's
  423), p50 412 / p95 654 ms through OpenRouter. The self-hosted models cost
  only GPU time: H2O answered at p50 296 / p95 550 ms on the 4070, Strands at
  941 / 1,721 ms (the optional fast kernels were not installed).
- **What it took to host H2O in 12 GB.** Its 9.3 GB of weights fit only with a
  4,096-token context, two sequences and no CUDA graphs. fp8 quantization
  was tried first and rejected: the model's own shim refuses it, because
  its probabilities drifted 0.107 from the release probes (tolerance 0.05).
  The bf16 setup passed that check.

Not tested, and why: Quyet-1.0-Large and deck-31B (31B, Gemma-4), Surogate
Rune 26B-A4B (26B, gated repository) do not fit a 12 GB card; Bespoke Labs'
Nimble-v4 and Nimble-v4-max are a hosted API that needs its own key. A
third-party leaderboard lists them (benchmarkheaven.com/jev-models); treat its
numbers as claims. Same caveats as sections 1 and 2.

## 5. Jev 1.14 and eight more models (2026-10-17)

Run through the same 2,132-request harness as sections 1 to 4, on the same day:
Jev 1.14 and eight models listed after 2026-10-09 or not yet run. All through
OpenRouter. Reference for the paired tests is Jev 1.13.

Accuracy, %:

| Model | Public: AG News / Banking77 / BoolQ | Fresh: Banking77 labels / reviews exact | Stress test: intents / yes-no / reviews exact / Polish all-correct | Stress test, pooled vs Jev 1.13 (only 1.13 right / only the model right) |
|---|---|---|---|---|
| Jev 1.13 | 88.5 / 80.5 / 89.0 | 99.3 / 98.0 | 98.3 / 100 / 100 / 97 | reference |
| Jev 1.14 | 88.5 / 81.0 / 89.0 | 98.7 / 98.0 | 98.3 / 100 / 98.8 / 96 | 2 / 0, p = 0.5 |
| Liquid D1 Ultra | 89.5 / 85.0 / 92.0 | 99.3 / 100 | 99.2 / 100 / 98.8 / 99 | 2 / 4, p = 0.69 |
| Span-02 | 88.5 / 84.0 / 89.5 | 97.4 / 96.0 | 97.5 / 100 / 95.0 / 95 | 11 / 3, p = 0.06 |
| Perplexity Decider 1.2 | 91.5 / 89.0 / 93.5 | 99.3 / 96.0 | 95.0 / 100 / 97.5 / 93 | 13 / 3, p = 0.02 |
| Nace Drex 2.0 | 91.0 / 80.5 / 91.0 | 96.1 / 85.0 | 93.3 / 99.2 / 85.0 / 90 | 31 / 5, p < 0.001 |
| Perplexity Decider Flash 1.2 | 90.0 / 87.0 / 91.0 | 100 / 81.0 | 95.8 / 100 / 73.8 / 89 | 33 / 1, p < 0.001 |
| Cloudflare Clef Omni | 90.0 / 94.5 / 85.5 | 97.4 / 94.0 | 95.8 / 91.7 / 88.8 / 88 | 37 / 3, p < 0.001 |
| ScaleDown Classify-1 | 88.0 / 75.0 / 79.5 | 92.8 / 89.0 | 97.5 / 92.5 / 91.2 / 85 | 37 / 3, p < 0.001 |
| Nace Drex 1.5 | 90.0 / 83.0 / 88.0 | 96.1 / 87.0 | 90.8 / 97.5 / 88.8 / 55 | 71 / 3, p < 0.001 |

- **Jev 1.14 is Jev 1.13 for practical purposes.** It differed on 2 of 500
  stress items, none of them in its favour, at the same price and token counts.
  The tail is tighter (p50 334 / p95 432 ms against 358 / 689 ms over the same
  requests) and more of its star scores clear 0.8 (94 % against 90 %).
- **Liquid D1 Ultra is the first rival of its maker that ties Jev on the
  stress test** (the original D1 trailed, 11 vs 2). It is clean on the traps
  that sank others: sarcastic reviews 20/20, Polish return-vs-complaint
  25/25, Polish injections 14/15 and English 10/10. It costs $0.0055 per 1,000
  AG News decisions (about a third of Jev) at p50 300 / p95 623 ms. It is
  under-confident on star scores (62 % of the hard reviews above 0.8). Its
  public Banking77 (85.0) rose to 99.3 on a fresh mirror.
- **Perplexity regressed.** Decider 1.2 is behind Jev on the stress test where
  the 27B v1.1 tied it (5 vs 5): telecom intents 95.0 against 99.2, English
  injections 6/10 against 9/10, Polish injections 9/15 against 15/15.
  Flash 1.2 trades accuracy for price: $0.0019 per 1,000 decisions, but
  73.8 % exact on hard reviews.
- **Span-02 learned Choice and Score** and is cheap ($0.002 per 1,000), but its
  p95 is 1.4 s and the stress test is an unclear tie (11 vs 3, p = 0.06).
- **Nace Drex 1.5 and 2.0, Clef Omni and ScaleDown Classify-1 are behind Jev**
  on the stress test. Drex 1.5 mislabelled Polish churn (62 %); Clef Omni, at
  $0.15 per million tokens, costs twice Jev per decision ($0.036 against
  $0.018) and looks trained on Banking77 (94.5 public, 97.4 fresh);
  ScaleDown has the slowest tail (p95 2.7 s), showed 67 % uptime on
  OpenRouter and returned a 504 on the first request.
- **ScaleDown's state must be a string or a text/document object**; the
  public Polish listing set, which sends an object state, failed with HTTP
  400 on all 144 requests.

Same caveats as sections 1 to 4.

## 6. basal-2.0, self-hosted Polish models (2026-10-19)

Run through the same 2,132-request harness on 2026-10-19: basal-2.0 4.5B and
basal-2.0-mini (Remek, Apache-2.0), built on SpeakLeash's Bielik and trained
on Polish and English typed decisions. They were served locally in Docker on
one RTX 4070 (12 GB). The latency is that GPU's, without network, and is not
comparable with the API rows. The large sibling basal-omni-1.0-ultra (31B,
about 62 GB in bf16) does not fit this card; JevBench measured it on
2026-10-17.

**How it was served.** The vendor's own engine never finished starting on
this card:
- the FP8 checkpoint stalled in torch.compile for over 50 minutes;
- `--mode fast-nocompile` was still capturing CUDA graphs after 18 minutes
  with the 12 GB nearly full.

So both models ran as the vendor's GGUF Q8_0 ports on llama.cpp (build
b11382), with basal-serve 2.1.0 in front (`--mode llamacpp`) and its
llama.cpp calibration file. The vendor reports that the Q8_0 port picks the
same option as bf16 on 98.4 % of decisions. llama.cpp's host-memory prompt
cache (8 GiB by default) had to be capped, because it got the server
OOM-killed in a 7 GB WSL VM.

Accuracy, %:

| Model | Public: AG News / Banking77 / BoolQ | Fresh: Banking77 labels / reviews exact | Stress test: intents / yes-no / reviews exact / Polish all-correct | Stress test, pooled vs Jev 1.13 (only 1.13 right / only the model right) |
|---|---|---|---|---|
| Jev 1.13 | 88.5 / 80.5 / 89.0 | 99.3 / 98.0 | 98.3 / 100 / 100 / 97 | reference |
| H2O-Lightning-4B (section 4, for comparison) | 88.0 / 91.0 / 86.0 | 98.7 / 89.0 | 97.5 / 98.3 / 87.5 / 84 | 27 / 1 |
| basal-2.0 4.5B (GGUF Q8_0) | 90.5 / 76.5 / 83.0 | 93.4 / 94.0 | 95.0 / 87.5 / 96.2 / 85 | 39 / 1, p < 0.001 |
| basal-2.0-mini (GGUF Q8_0) | 86.5 / 74.0 / 78.0 | 86.8 / 81.0 | 88.3 / 68.3 / 80.0 / 65 | 105 / 1, p < 0.001 |

- **basal-2.0 4.5B is behind Jev, and level with H2O on Polish.** On the
  Polish stress-test tickets it got 85 % fully right (Jev 97 %, H2O 84 %).
  The misses were:
  - return vs complaint: 20/25;
  - negated refund: 12/15;
  - slang without diacritics: 12/15;
  - Polish injections: 14/15, as good as Jev.

  On the public Polish listings its Nouls matched Jev (97.2 %).
- **Its strength is star scores and sarcasm.**
  - Reviews: 96.2 % exact on the stress test and 94 % fresh, against H2O's
    87.5 % and 89 %.
  - Sarcastic reviews: 19/20.
- **Its weakness is reading a passage.** On stress-test yes/no it scored
  87.5 %, and on public BoolQ 83.0 against Jev's 89.0 (p = 0.03). Inside the
  passages it got date order 17/20, number comparison 17/20 and long
  distractor passages 21/24. Fresh Banking77 labels were 93.4 against 99.3
  (p = 0.01).
- **No sign of public-set training.** Its public Banking77 (76.5) is below
  Jev's, and it gained +16.9 points on the fresh mirror.
- **Very cautious confidence.** The card itself says the calibration is
  cautious on unseen tasks. On the stress test, 12 % of reviews, 43 % of
  yes/no answers and 66 % of Banking77 answers cleared 0.8; at that gate
  99–100 % were right. Expect a large review band unless you fit thresholds
  on your own data.
- **basal-2.0-mini is far behind**: Polish all-correct 65 %, Polish
  injections 7/15, stress-test yes/no 68 %.
- **Speed on this setup:**
  - 4.5B: p50 580 / p95 1,943 ms. In the GGUF modes basal-serve sends the
    prompts of one request one after another (vendor docs), and four
    llama.cpp slots shared the GPU.
  - mini: 290 / 973 ms.
  - The vendor reports 25–30 ms per question on an H100 with its own engine.
    That is a different setup, not reproduced here.

Same caveats as sections 1 and 2.
