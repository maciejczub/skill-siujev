# Evidence: what is claimed, what is measured, and by whom

## Contents
- Labels: [VENDOR], [INDEP], [CUSTOMER]
- 1. Accuracy: vendor eval, head-to-head with frontier and cheap models
- 2. Calibration and consistency
- 3. Latency
- 4. Cost
- 5. Operations and access
- 5b. This skill's own pilot on Polish text (2026-09-21)
- 5c. Community builds
- 5d. Decision models compared: JevBench, this skill's benchmark, what holds
- 6. What nobody has measured yet

Compiled 2026-09-21, six days after Jev's release; decision-model benchmark
comparison (5d) built 2026-10-01 to 10-19 and condensed on 2026-10-19, when
JevBench became the place for rankings. Everything below is either
**[VENDOR]** (TypeSafe's own numbers), **[INDEP]** (someone outside TypeSafe
measured it), or **[CUSTOMER]** (a user quoted in press without a public
method). When you use a number in a verdict, carry its label with it. Most of
the independent work is a single person's repository run over a few thousand
calls; treat each as one data point, not a consensus.

## 1. Accuracy

**[VENDOR] TypeSafe's launch eval (4 workflows, labels = average of two frontier
LLMs, workflows written by TypeSafe's own team, bias acknowledged).**
Jev 67.8 % overall vs 74.1 % for the best frontier model; GPT-5.6 Terra 67.9 %.
Per workflow: security triage 61.7 % (Opus 5: 66.2 %), invoice processing
61.8 % (Sol 79.1 %), customer service 76.0 % (78.3 %). Sonnet 5 scored 67.8 %
and Luna 66.8 % on the same eval; LLM structured-output type-error rates in the
same material ran 0.58–45.5 % (Haiku 4.5 the worst) against Jev's 0 % by
construction. Cost per case: Jev $0.0004,
Terra $0.0304, Opus 5 $0.1761; time per case 0.4 s, 10.1 s, 37.8 s.
Read: on the vendor's own tasks Jev sits at the accuracy of a **mid-tier LLM**,
clearly below frontier, and the gap is largest on document-heavy extraction
(invoices). That is the tier to price against.
Sources: typesafe.ai/blog/introducing-system-one-models-and-jev; datacamp.com/blog/system-one-models-jev; ts2.tech (2026-09-17) on the self-tested nature.

**Head-to-head with frontier models (GPT-5.6 Terra/Sol, GPT-6 Astra, Claude
Opus 5 / Sonnet 5 / Fable 5.1, Gemini 3.8 Flash).** A common claim online is
"Jev performs at GPT-5.6 Terra level". The published comparisons, by task type:

| Task (n) | Jev | Frontier | Who |
|---|---|---|---|
| TypeSafe 4-workflow eval, LLM-averaged labels (n not published) | 67.8 % | Terra 67.9, Sonnet 5 67.8, Luna 66.8, Opus 5 73.1, Sol 74.1 | VENDOR |
| … invoice processing | 61.8 % | Sol 79.1, Opus 5 78.4 | VENDOR |
| AG News 4-class topic, ground-truth labels (100,000) | 89 %, 40 s, $0.50 | Terra 88 %, 32 min, $37.58 | PARTNER (MotherDuck) |
| Banking77 8-way (160) / 77-way (231) | 83.8 / 78.8 % | Terra 89.4 / 84.0; GPT-5.4 nano 90.0 / 78.4 | INDEP (ayautomate, 3,955 calls) |
| Prompt-injection detection (400) | 87.0 % | Terra 86.8, Haiku 4.5 89.0 | INDEP (ayautomate) |
| Banking77 (300) / SST-5 (300) / IMDB (300) | 0.780 / 0.570 / 0.970 | Terra 0.847 / 0.593 / 0.970 | INDEP (4esv, one run) |
| BoolQ + Banking77 + Yelp + ChaosNLI (200) | 72.5 % | Fable 5.1 84.0, Astra 79.0, Kimi K3 74.5, DeepSeek V4.1 Flash 76.0 | INDEP (manjunathshiva) |
| … calibration on the same 200 | ECE 0.161 | Fable 5.1 0.064, Astra 0.119 | INDEP (same) |
| Commit-message classification (800) | 65.8 % | Opus 5 63.5, GPT-5.6 59.5, Haiku 54.6 | INDEP (primeline, pre-registered) |
| Knowledge-base category (450) | 90.7 % | GPT-5.6 92.7, Opus 5 86.9, Haiku 97.8 | INDEP (primeline) |
| Claim-support "does the source say it" (42) | 85.7 % | Sonnet 5 85.7, Gemini 3.1 Pro 81.0 | INDEP (TheWayWithin) |
| Synthetic support tickets, 5 queues (100) | 92 % | Sonnet 5 96, Opus 5 94, Gemini 3.8 Flash 95–96, Grok 4.6 93 (all ties at n=100) | INDEP (DevX) |
| Python code-review rule compliance (360) | 98.0 % | Fable 5.1 100, Gemini 3.8 Flash 100; cost/1k $0.043 vs $11.78 vs $1.94 | INDEP (gemanor) |
| Agent-eval judge vs human oracle (500) | 100 % | Terra 99.8, Luna 96.4, Sonnet 4.6 80.0; Jev's score variance 900x lower | INDEP-ish (LangChain) |
| PubMedQA yes/no (300 × 5) | 91.3 % | Gemini 3.8 Flash 92.5 | INDEP (Jevals) |
| Portuguese court sentences, 12 fields (120) | 96.6 % | Gemini 3.8 Flash 98.8, Luna 96.8 | INDEP (lab-dados) |
| Writing-defect detection (12 passages, 7 defects) | 6/7 at 0.35 s | Fable 5.1 7/7 at 8.8 s | INDEP (Every) |
| Cascade Jev → Terra at confidence 0.80 (160/231) | 90.0 / 84.8 % at 26–28 % of Terra's cost | Terra alone 89.4 / 84.0 | INDEP (ayautomate) |
| Cascade Jev (p ≥ 0.9) → Fable 5.1 (200) | 82.5 % at 37 % of Fable's cost | Fable alone 84.0 | INDEP (manjunathshiva) |

Read across these (every independent test is a single run, n ≤ 500 except
MotherDuck's, so ±5–10 points is noise):

- **Short inputs, few crisp labels** (routing, spam, topic, yes/no on a
  paragraph, rule compliance, pass/fail judging): Jev is inside noise of
  Terra and usually of Opus 5 / Sonnet 5 / Gemini 3.8 Flash, at −2 to +1
  points. "Terra level" is fair here.
- **Many overlapping labels** (Banking77 77-way): 5–7 points behind Terra,
  4 behind Gemini 3.8 Flash; confident errors land on near-duplicate intents.
- **Long, fuzzy, multi-field judgments** (invoices, mixed benchmarks with
  ambiguity, star ratings): 5–6 points behind Sol / Opus 5 overall, 17 on
  invoices (vendor eval); 6.5–11.5 behind Astra / Fable 5.1 in the one
  independent test, with the worst calibration of the six models tested.
- **Long-list reranking**: not a contest, per-passage calls and 2–3 points
  under cheap flash models.
- **Cascades close the gap**: Jev first, a frontier model for the
  low-confidence 20–37 %, lands within 1–2 points of the frontier model at
  26–37 % of its cost.

**[INDEP] Head-to-head with cheap LLMs on short classification tasks.**
- DevX Labs (2026-09-20), 100 synthetic support tickets, 5 queues, 20 models,
  JSON mode, temperature 0: Jev 92 % at $0.0185 per 1k tickets and 385 ms;
  DeepSeek V4.1 Flash (low reasoning) 97 % at $0.026 and 1.7 s; GLM-5.3 Flash
  low 94 % at $0.021 and 0.9 s; Qwen3.8 Flash low 90 % at $0.026; Mistral
  Small 4 79–86 %; Sonnet 5 96 % at $0.54; Opus 5 94 % at $2.44. With n=100,
  17 of Jev's 18 pairwise comparisons are statistical ties; the only clear win
  is over Mistral Small. Billed cost differed from list price by 8–81 % for
  half the models. Source: github.com/rachit-srivastava-devx/jev-classification-benchmark
- Same authors, RAG rerank (pick best 5 of 100 BM25 chunks, 350 questions):
  GLM-5.3 Flash 36.9 %, Qwen3.8 Flash 36.1 %, DeepSeek 35.9 % in one call
  each at $3–5 per 1k questions; Jev per-passage Score/Noul 33.4–33.7 % at
  $2.7–2.8 but 100 calls and ~6.8 s per question; Jev Choice over all 100
  chunks in one call failed on 85 of 350 questions because the input exceeded
  the ~32k ceiling. Long-list reranking is not a Jev win.
- JevBench v1.0 (2026-09-19, 242 decisions): GPT-5.6 Luna low 97.1 % at
  $0.176 per 1k; Jev 96.3 % at $0.027 and 0.65 s; DeepSeek V4.1 Flash and
  Gemini 3.1 Flash-Lite 95.5 %; a self-hosted Qwen3.6-35B logit adapter
  95.5 % at 0.68 s. Source: benchmarkheaven.com/jev-models/v1
- Supa Journal (Japan, 208 cases, 4 tasks): Jev 95–100 % vs Haiku 4.5
  92.5–96.9 %, GPT-5.6 Luna 97.5–100 %, Gemini 3.5 Flash-Lite 81–100 %, Qwen3.7
  Flash 82.5–95 %. Jev p50 330–350 ms vs LLMs 930–1,430 ms. Cost per 1k
  items: Jev $0.019–0.033, Qwen3.7 Flash $0.012–0.023 (cheaper than Jev),
  Luna $0.07–0.13, Haiku $0.54–0.92. Jev's ECE 0.002–0.047, Gemini's up to
  0.163. Author: "the case for Jev is agility, not accuracy."
  Source: journal.supa.ai/jev-classifier-benchmark/
- Aman Kumar, public datasets: Enron spam Jev 98.7 % (GPT-5.4-mini 97.7,
  GPT-5.6 Luna 98.0); SST-2 95.7 (92.7 / 93.0); AG News 91.3 (88.3 / 89.7);
  Banking77 77-way intent 76.0 (78.7 / 81.7). When Jev is confident it is
  right 90–99.6 % of the time at 66–90 % coverage. Jev median latency
  0.8–0.9 s from that location. Conclusion: strongest on short inputs with
  crisp labels, loses ground as inputs get longer and labels fuzzier.
  Source: amankumar.ai/blogs/jev-measured
- Arize / NearHere: listing moderation Jev 96 % vs Gemini Flash-Lite 86 %, 85
  input tokens vs 910; spam on 18.5k emails: Jev zero-shot 98.3 % vs TF-IDF +
  logistic regression trained on 14.8k labels 98.4 % (a tie). Calibration:
  emails scored < 0.1 were spam 0.1 % of the time, ≥ 0.9 were spam 99.9 %.
  Source: arize.com/blog/typesafe-jev-llm-judge/
- Read across these: on short-input, few-label tasks Jev sits in the same
  band as GLM-5.3 Flash, Qwen3.8 Flash, DeepSeek V4.1 Flash, Gemini
  Flash-Lite, GPT-5.6 Luna (low) and Haiku 4.5, at 3–15x lower cost per
  decision than most of them and 2–5x lower latency. It trails on long fuzzy
  single-shot judgments and on 77-way intents.

**[INDEP] Decomposition is the whole game (beri.net, 2,000 phishing emails).**
One question "is this phishing?": Jev 62.6 % vs Claude Haiku 4.5 81.3 %. Five
atomic questions plus a logistic regression fitted on 1,000 labelled emails:
Jev 95.0 % vs Haiku 93.2 %. Cost per 1,000 emails: Jev $0.038, Haiku $0.46
(single) / $1.02 (five). The author's own caveat: "the 95 % is not Jev, it is
Jev plus your labelled data plus a regression you maintain."
Source: beri.net/article/typesafe-jev-typed-decision-model-calibration-decomposition-shadow-eval

**[INDEP] Zero-shot vs encoder baselines (zhuyansen).** Jev beat NLI-DeBERTa
zero-shot and bge-m3 embedding classification on all seven sets (AG News 0.865
vs 0.763/0.777; SST-2 0.960 vs 0.913/0.864; Banking77 0.712 vs 0.579/0.722;
TweetEval-emotion 0.827; PAWS AUC 0.936; post-release arXiv 0.891 vs 0.589).
Estimated label-equivalence: Jev zero-shot ≈ a BERT fine-tuned on a few hundred
labels for AG News/Banking77 and on 2k+ labels for SST-2/TweetEval/PAWS.
Source: github.com/zhuyansen/jev-zeroshot-vs-bert

**[INDEP] Reranking (anessbelbati, 8 English sets, 1,617 queries, 30 BM25
candidates each).** Jev 4-level rubric nDCG@10 0.692 at 422 ms and $0.45 per 1k
queries; Cohere Rerank 4 Pro 0.691, 844 ms, $2.51; ZeroEntropy zerank-2 0.682,
1.8 s, $0.22; DeepSeek V4.1 Flash with JSON 0.682, 2.2 s, $1.13; BM25 alone
0.486. Difference to Cohere is within noise ("neither a winner nor
equivalence"). Datasets may be in training data.
Source: github.com/anessbelbati/jev-rerank-bench

**[INDEP] Prompt-injection detection (Gaurav-Gosain, 662 German-skewed
messages).** 96.5 % accuracy, F1 95.6 %, ROC-AUC 0.993, ECE 0.059; adding the
deployment context to the state lifted accuracy from 89.7 % to 96.5 %.
Vulnerable-code pair ranking: vulnerable twin ranked higher in 89 % of 200
pairs. Source: github.com/Gaurav-Gosain/jev-sec-bench

**[INDEP] Model routing cascade (FirasSX914/Janus).** Banking77: route to
DeepSeek when Jev confidence < 0.67 gave 88.4 % at 53 % lower cost than the
LLM alone and 302 ms median vs 2.3 s. Web of Science: no threshold beat the
single LLM ("DO NOT ROUTE"). The optimal threshold moved between datasets
(0.67 vs 0.37). Source: github.com/FirasSX914/Janus

**[INDEP] Community leaderboard (JevBench v1.2.3, 534 decisions).** Jev 1.13
ranks first on a composite of accuracy, calibration, speed, cost (75.4), but
open 4B-class systems built on Qwen3.5-4B (74.7), DiffusionGemma (74.3), and
GLiNER2 are within 1–4 points. Source: github.com/fstandhartinger/jevbench

**[INDEP] Open-source rival Laya (ModernBERT-large 421M, Apache-2.0).** Its
author reports 0.766 vs Jev 0.727 on 2,000 typed decisions, with better Brier
and ECE, at 33–40 ms on a T4 and 100+ languages; a separate tester got Laya at
0.590 vs Jev at higher accuracy, 30 ms vs 302 ms. Conflicting; treat as "a
self-hosted encoder can be competitive on latency and sometimes accuracy".
Sources: github.com/NandhaKishorM/laya; gadgetpilipinas.net (2026-09)

**[VENDOR] Cookbook results (docs.typesafe.ai/cookbooks, small runs replayed
from cached responses; useful for what the shape of a result looks like, not
as accuracy guarantees).**
- Parallel questions: 13 questions over a 54k-character article in one call
  cost $0.0005 and took 0.27 s vs $0.0061 and 2.7 s as 13 calls; answers
  identical. (12.2x cheaper, 10x faster.)
- Consistency: an 8-Choice moderation rubric ran at 114 ms and $0.000046 per
  call with probability std 0.01 across 15 repeats; LLM rubric calls took
  0.8–13.9 s at 20–900x the cost. Raw label agreement 90.8 %, 99.2 % after
  abstaining below 0.60 top probability (25.8 % abstained). Two of eight
  questions still flipped labels near the threshold.
- 75-way SIC industry classification: forced accuracy 65 %; 90 % on the half
  with confidence ≥ 0.9, 40 % on the rest, which was reported at the coarser
  division level instead (70 % there). The value is in the gate, not the raw
  accuracy.
- Legal passage reranking (one Noul per query-candidate pair, BM25 top-30):
  top-1 5 % → 18 %, top-10 38 % → 62 %; 1,200 calls cost $0.065.
- Hierarchical taxonomy walk: beam search K=3 got 4/4 leaves, greedy 2/4 (four
  examples only).
- Skill suggestion over 182 skills, two-stage: wrong loads 16.8 % → 7.3 %
  (oracle 2.5 %), needless loads 9.8 % → 4.0 %.
- Feature extraction for CatBoost: 38 Jev questions cut held-out RMSE from 2.15
  (one Score) to 1.77.
- Per-field verifier Nouls in an extraction cascade separated errors at
  0.85–0.95 where a single holistic "is this extraction good?" Noul gave 0.56.
- Eight cookbooks (RAG passage filter, date extraction, entity alignment,
  function calling, hierarchical classification, guardrails, value extraction,
  line search) publish no cost or latency numbers.

## 2. Calibration and consistency

**[INDEP] Calibration audit (jujumilk3, ~7,000 calls).**
- With an explicit `unknown` option Jev chose it for 95 % of 300 unanswerable
  items (ECE 0.023). **Without that option accuracy on the same items fell to
  0 %** and it picked a stereotype at 0.79 average confidence (ECE 0.79).
  Always give an out.
- Korean vs English instructions on identical items: ECE 0.076 vs 0.075.
- Noul(A) + Noul(not A) sums ranged 0.71–1.42; Noul vs two-option Choice
  differ by 0.125 on average. Matches the vendor's "no structural invariants".
- Option-order bias: none observed in one test (0 argmax flips in 400). TypeSafe's
  own failure-mode page, reviewed 2026-10-02, now says Jev 1.13 leans toward the
  first option in some cases, so check order on your own data.
- 16 questions bundled vs 1: confidence shift 0.008, answers flip 0.4 %.
  Bundling *questions* over one state is safe.
- **Non-determinism**: 50 identical requests gave 15 distinct answers
  (small numeric drift, not label flips in that test). Do not assume
  replay-stable outputs; log the response.
- Option-text leakage: with the question removed, options alone still
  predicted 0.38–0.46 (chance ≈ 0.15). Criteria wording carries signal.
Source: github.com/jujumilk3/jev-calibration-audit

**[INDEP] Ranking bench (yodablocks).** 20 Newsgroups: ECE 0.045, passes all
gates. Amazon ESCI (product relevance): ECE 0.242, 4-way accuracy 0.49, fails
four of six gates, systematically **underconfident**. Two practical findings:
probabilities are returned with **two decimals** (53 of 360 rows tied at 0.99,
so top-k order among ties is arbitrary), and **packing 40 rows into one state**
to rank them shifted probabilities by 0.26 on average and dropped Spearman
from 0.93 to 0.58. Batch questions, not items-to-be-ranked, into one state.
Source: github.com/yodablocks/jev-orderby-bench

**[INDEP] OpenProse "Programming with classifiers" (2026-09-18, code-evidence
retrieval over Flask).** Two-stage judge (compact descriptions, then bodies)
kept all 32/32 required evidence sets vs 27/32 for a lexical baseline, at 3.3 %
fewer input tokens than judging bodies directly. Scores were not stable
properties of items: batch composition moved scores more than repeats did.
Larger candidate pools were not monotonic (64→128 helped, 256 hurt). A local
MiniLM reranker did not beat Jev on this cohort. Source:
research.prose.md/articles/programming-with-classifiers/

**[INDEP] Quick tests (Interesting Engineering substack).** Negating the
request moved a refund probability from 0.98 to 0.03 (good). A forced 3-option
Choice with no valid answer still returned one of them at confidence 0.31
(again: add `none`). Most of the batching saving comes from encoding the state
once. Roughly 5x faster and 8.6x cheaper than Mistral Small 4, 1.6x cheaper
than DeepSeek V4.1 Flash on their task.

## 3. Latency

**[VENDOR]** "70–500 ms end to end"; "most queries about 100 ms"; homepage
0.114 s vs 8.566 s for GPT-5.6 Terra on a Doom-playing demo.

**[INDEP]** p50 280 ms / p95 397 ms (Seoul); median 239 ms (France); p50 325 ms
(sec-bench); 422 ms per 30-doc rerank query (Algeria); 256 ms median per paper
(flaviocopes); 302 ms median (Janus); 0.64–0.67 s median (Japan, Classmethod);
tweet aggregate median 76 ms across 333 reported figures. Sequential throughput
about 17 decisions/s; 64-way concurrency turned a 40 s job into 7.6 s
(MindStudio). **No sustained-load test under production traffic exists.**
Plan with 250–350 ms p50 from Europe/Asia and measure your own p95.

## 4. Cost

**[VENDOR]** $0.042 per M input tokens, output free. "444.6x cheaper" is the
top of their own workflow set; against the accuracy-comparable Terra the same
table gives roughly 25x faster and 76x cheaper (pearpages' reading).

**[INDEP] / [CUSTOMER]** examples: $0.0399 per 1,000 decisions at ~950 input
tokens each (JevBench); $0.013 for 359k tokens (yodablocks); 1,709 judgments
for under a cent (Every); $0.00007 per PR review; 10,000 social posts/day for a
month ≈ $5.42 (OpenTweet); Vercel: 5–18x faster than an OpenAI safety
classifier; Bryo AI on email classification: TechCrunch quotes them as 10–20x
cheaper than Gemini, while the ayautomate build index records the same company
as "slightly more accurate but 10–20x more expensive"; the two reports conflict
and neither is verifiable, so do not cite Bryo either way.
Tweet-aggregate medians: 7x faster, 30x cheaper than whatever users replaced.
MindStudio: comparable to Gemini Flash-Lite at small inputs, gap widens with
input size (because Jev bills input only and charges nothing for output).

Cost scales with the number of **states** (rows, pairs, passages), not with
questions: reranking costs queries × shortlist size requests; a RAG filter
costs k requests per query; feature extraction over 100k rows is 100k requests
per round. In practice cookbooks ran 4–12 worker threads and one notes the
public endpoint rate-limits "above roughly eight" concurrent calls on a
shared key.

Costs that are *not* in the $0.042: building the labelled pilot set, tuning
thresholds, the review queue for uncertain cases, and the fallback path.

## 5. Operations and access

- Direct API is **waitlist-gated** as of launch; Vercel AI Gateway, OpenRouter
  (`typesafe/jev-1.13`, 32k context, same price, latency stats not published)
  and Cloudflare AI list it without a waitlist. Pricing page on typesafe.ai
  returns 404; the price lives on the homepage and docs/models.
- Free credit: one secondary source claims $5 on signup; two others say none
  published. Unverified.
- **No SLA**. Status page shows 99.854 % over 90 days before launch and a
  demand-driven outage on launch day. Rate limits "adjusting dynamically",
  and they did: 250k tokens/s and 1,200 req/min at launch, 100k tokens/s and
  40 req/s on 2026-10-01 [VENDOR, docs/models].
- Hosted in the US, multi-region; **no EU data-residency option found**. Not
  trained on customer data; ZDR for enterprise only; default retention window
  for ordinary accounts not stated. No on-prem, no open weights, no paper.
- Not deterministic; no prompt caching (OpenRouter: not supported; JS SDK issue
  open). Choice is single-select; multi-label means one Noul per label.
- Integrations exist for LangChain (`langchain-typesafe`), Pydantic AI
  (`TypeSafeModel`), LiteLLM, and community SDKs in Go, Java, PHP, Ruby, Rust,
  .NET, Elixir. TypeSafe's `system-one-adapter-python` is an LLM-backed drop-in
  with the same client interface, useful as a **fallback path** if Jev is
  unavailable (no benchmark numbers published for it).
- Languages: docs say English primary, others "not equally well"; Korean
  calibration parity and a German injection corpus at 96.5 % are the only
  non-English measurements found. **No Polish evaluation exists.**

## 5b. This skill's own pilot on Polish text (2026-09-21) [INDEP, small]

Run by the skill's author with `scripts/probe.py --openrouter --repeats 3`
on 48 synthetic Polish marketplace listings (7 weapons, 8 counterfeit, 7
restricted medicine, 26 allowed, including hard negatives such as an airsoft
replica, a 16 J air rifle, a kitchen knife, a decorative katana, OTC
ibuprofen, supplements, and three obfuscated positives like "br0ń",
"k@rabinek", "pytaj na priv"). Questions in English, state in Polish: three
Nouls (one per category) and one Choice with an `allowed` option. The spec is
bundled as `assets/pilot-spec-example.json`. 144 requests, ~740 input tokens
each, billed $0.0045 in total.

| Question | Agreement with labels | Uncertain band (0.35–0.65) | Flips across 3 repeats |
|---|---|---|---|
| weapons (Noul) | 144/144 | 0 | 0/48 |
| medicine (Noul) | 144/144 | 0 | 0/48 |
| counterfeit (Noul) | 132/144 (92 %) | 3 | 0/48 |
| category (Choice, 4 options) | 128/144 (89 %) | 18 below 0.5 confidence | 1/48 |

- **Confidence gating worked.** Choice answers at confidence ≥ 0.5 were right
  118/126 (94 %); below 0.5 only 10/18 (56 %). Every distinct Choice error had
  confidence 0.40–0.55, so a 0.6 review threshold would have caught all of
  them at the cost of reviewing ~15 % of items.
- **Nouls beat the Choice on hard negatives**, as the docs predict (Choice is
  relative and must pick something). The airsoft replica got weapons Noul
  0.06 but the Choice said `weapons` at 0.58; the air rifle 0.14 vs `weapons`
  0.66; OTC ibuprofen 0.05 vs `medicine` 0.55. Use per-category Nouls for the
  decision and the Choice only as a tie-break or summary.
- **Literal reading showed up once**: "Replika ASG Glock 17" got counterfeit
  0.91 (the words "replika" and "Glock" taken at face value). Two of the other
  counterfeit misses were arguably label errors in the pilot set (Kamagra is
  an unlicensed copy; a "genuine but bought at a bazaar" pair is ambiguous).
- **Obfuscated positives were all caught** at 0.85–0.98.
- **Latency from Poland via OpenRouter**: 30 sequential short requests p50
  368 ms, p95 449 ms, max 518 ms; the 740-token pilot requests p50 389 ms, p95
  521 ms, max 1.4 s.

Read this as "English questions over short Polish product text work at least
as well as the English benchmarks on similar tasks", nothing more: 48
synthetic items written by one person, one domain, no long or messy text, no
real seller adversarial behaviour. A real pilot needs the marketplace's own
listings and labels.

## 5c. Community builds

The skill's use-case catalog lists what people have built in the first week, by
capability family, with the builders' own numbers, and a "Where it fell
short" section (reranking over 33k entries lost to vectors; CSV column typing
cost 6.6–12.7x an LLM; an independent intent-routing benchmark found 3.6x
faster and 40–49x cheaper than GPT-5.6 Terra with lower accuracy, not
193.6x/444.6x; Spanish input cost 3–6 accuracy points). Treat those as
[CUSTOMER] unless marked measured.

## 5d. Decision models compared: where to look and what holds (as of 2026-10-19)

Two independent sources measure decision models against Jev. They measure
different things; use the one whose tasks look like yours, then pilot.

**JevBench** (Benchmark Heaven) [INDEP]: https://benchmarkheaven.com/jev-models
(open weights) and https://benchmarkheaven.com/jev-models/api (hosted APIs);
repository https://github.com/fstandhartinger/jevbench. The broadest and most
current source: board v1.7.46 of 2026-10-18 lists 258 systems, 46 of them
hosted APIs. Its items are sealed. Its scores cover four axes, Intelligence,
Calibration, Speed and Cost, plus a composite, a Capability score and a
23-language view. It also measures the 26–31B open models that need a large
GPU. Use it to find which models exist, how they compare on calibration,
latency and cost, and which self-hosted ones deserve a pilot. Three caveats:

- **Its Intelligence axis leans on reasoning**: math (129 of the 534 items in
  v1.2), multi-hop questions, long policies, dates and numbers. TypeSafe
  says to keep such tasks out of Jev, so general LLMs score about 95 there
  and Jev about 64. A high Intelligence score says a model reasons. It does
  not say the model classifies your tickets better.
- **Its language cells are reasoning items too.** The Polish cell has 88
  items, and Jev 1.13 scores 22 there. In this skill's benchmark Jev got
  96–97 % of Polish tickets fully right. Both results are true; they answer
  different questions.
- **The composite rests on weights, caps and cost estimates.** Self-hosted
  rows are priced at an estimated GPU rate. The method changes often, and the
  maintainers warn against comparing scores across versions. Quote the board
  version and its date.

**This skill's benchmark** [INDEP]. It ran from 2026-10-01 to 10-19 and is
now frozen; the full tables are in the skill repository
(`docs/decision-model-benchmark.md`) and are not loaded with the skill. It
covers the jobs decision models are meant for and nothing else:
- intents (19- and 77-way), star scores, yes/no reading over a passage,
  Polish support tickets and Polish marketplace listings;
- public sets, fresh unpublished mirrors as a contamination check, and a
  500-item stress test built on named traps;
- paired McNemar tests against Jev 1.13.

Stress test, 500 items, short texts:

| Model | Only Jev 1.13 right / only the model right | Polish tickets, all labels right | Cost per 1,000 AG News decisions | p50 / p95 |
|---|---|---|---|---|
| Jev 1.13 | reference | 97 % | $0.018 | 341 / 458 ms |
| Jev 1.14 | 2 / 0 (tie) | 96 % | $0.018 | 334 / 432 ms |
| Liquid D1 Ultra | 2 / 4 (tie) | 99 % | $0.006 | 300 / 623 ms |
| OpenAI Decisions | 5 / 3 (tie) | 96 % | $0.021 | 437 / 720 ms |
| Perplexity Decider 27B (v1.1) | 5 / 5 (tie) | 99 % | $0.004 | 602 / 1,068 ms |
| GPT-6 Luna (LLM, chat, reasoning off) | 7 / 4 (tie) | 99 % | $0.026 | 1.2 / 1.7 s |
| Span-02 | 11 / 3 (p = 0.06) | 95 % | $0.002 | 292 / 1,406 ms |
| Liquid D1 | 11 / 2 | 91 % | $0.005 | 424 / 992 ms |
| Perplexity Decider 1.2 | 13 / 3 | 93 % | $0.004 | 392 / 502 ms |
| Cloudflare Clef | 13 / 0 | 90 % | $0.012 | 569 / 1,379 ms |
| Mercury Decide (free and paid) | 15 / 5 and 16 / 5 | 89 / 88 % | free / $0.004 | 389 / 575 ms |
| Microsoft Decision-1 | 25 / 5 | 88 % | $0.005 | 412 / 654 ms |
| Cloudflare Clef Flash | 26 / 1 | 86 % | $0.006 | 534 / 1,564 ms |
| H2O-Lightning-4B (self-hosted) | 27 / 1 | 84 % | GPU time | 296 / 550 ms (RTX 4070) |
| Nace Drex 2.0 | 31 / 5 | 90 % | $0.007 | 378 / 964 ms |
| Perplexity Decider Flash 1.2 | 33 / 1 | 89 % | $0.002 | 296 / 396 ms |
| Tev1 4B (no 77-way items) | 35 / 0 | 86 % | $0.009 | 340 / 566 ms |
| Cloudflare Clef Omni | 37 / 3 | 88 % | $0.036 | 323 / 549 ms |
| ScaleDown Classify-1 | 37 / 3 | 85 % | $0.015 | 483 / 2,708 ms |
| basal-2.0 4.5B (self-hosted, GGUF Q8_0) | 39 / 1 | 85 % | GPU time | 580 / 1,943 ms (RTX 4070) |
| Solar Decide (no 77-way items) | 56 / 1 | 70 % | $0.022 | 720 ms / 12.5 s |
| Kev 4B | 62 / 5 | 75 % | $0.005 | 619 / 901 ms |
| Nace Drex 1.5 | 71 / 3 | 55 % | $0.005 | 544 / 1,203 ms |
| Solar Decide Flash (no 77-way items) | 93 / 0 | 51 % | $0.022 | 905 / 1,646 ms |
| Strands Decider 2B (self-hosted) | 105 / 1 | 62 % | GPU time | 941 / 1,721 ms (RTX 4070) |
| basal-2.0-mini (self-hosted, GGUF Q8_0) | 105 / 1 | 65 % | GPU time | 290 / 973 ms (RTX 4070) |
Ties are p > 0.05; every other row is behind Jev at p < 0.05. Span-01 takes
Noul questions only and was behind on yes/no reading (29 / 3).

What held across every round, and is worth carrying into a verdict:

- **Clean, short items do not separate the good models.** On ordinary public
  and fresh items most models were within noise of Jev. The differences
  showed on traps:
  - sarcastic reviews;
  - Polish return-vs-complaint tickets;
  - injected instructions;
  - text without diacritics;
  - "other" messages full of domain words.

  Put the hardest, messiest and non-English items into a pilot.
- **Training on the target language did not beat Jev on it.** basal-2.0
  4.5B is built on Bielik and trained on Polish and English decisions, yet
  it got 85 % of the Polish stress-test tickets fully right against Jev's
  97 %. It lost on return-vs-complaint (20/25), negated refunds (12/15) and
  slang without diacritics (12/15). It was strong on star scores (96 % exact)
  and sarcasm (19/20). It is also very cautious: only 12 % of hard reviews
  and 43 % of hard yes/no answers cleared 0.8, though nearly all of those
  were right. A language-specific model still needs the same pilot.
- **A lead on a public benchmark often did not survive fresh text.** Clef, Clef Omni,
  Microsoft Decision-1, H2O and Strands beat Jev on public Banking77, then
  gained far less than Jev on a fresh mirror with the same 77 labels (Clef
  +1.4 points against Jev's +18.8). Never choose a model on public-set scores.
- **Versions move, and not always upward.** Jev 1.14 equals 1.13.
  Perplexity's 1.2 is worse than the v1.1 it replaced, and its `latest` alias
  already points to 1.2. Pin model ids and re-run the pilot on every upgrade.
- **Confidence does not transfer between models.** Kev and D1 Ultra are
  under-confident on some tasks and Solar is overconfident. A threshold tuned
  on one model is wrong for another, including a fallback.
- **Providers count tokens differently.** For the same AG News request Jev
  counted 423 input tokens and D1 131. OpenAI counted 876 for a Polish ticket
  where Jev counted 736. Compare cost per decision, never price per token.
- **Contracts bite before accuracy does.** Watch for:
  - option caps (Tev1 20, Solar 26);
  - accepted state types (ScaleDown, Span-01);
  - refusals (OpenAI);
  - free-tier request caps (Mercury).
- **The two leaderboards disagree where their tasks differ.** OpenAI
  Decisions is 15th on JevBench's API board (Intelligence 57 against Jev's
  64) and ties Jev here. The original Liquid d1 ranks above Jev on JevBench
  and fell behind it here on Polish traps.

Caveats: one author; items written by one LLM family and labelled blind by
two others; short texts only; one client location; prices as of each run.

## 6. What nobody has measured yet (as of 2026-10-19)

- Sustained-load latency.
- Head-to-head comparisons with Llama Guard, Cleanlab, Katanemo Arch, Fastino,
  Voyage rerank and SetFit.
- Polish or other Slavic languages beyond the two small sets above: long
  text, real seller data, other domains.
- Default data retention.
- Long-run price stability.
- Decision models on long, messy, multi-field documents in in-scope tasks
  (this skill's benchmark used short texts; JevBench's long-policy items test
  reasoning), and on arithmetic, counting or date windows.
- OpenAI's Decisions API through its native `/v1/decisions` endpoint (this skill's
  benchmark used OpenRouter's wrapper), its image input, and the Lite tier of Span-01.

If a verdict depends on one of these, it is PILOT FIRST.
