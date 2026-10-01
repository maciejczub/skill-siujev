# Jev use-case catalog (skill reference)

What people have actually built with Jev (TypeSafe AI's typed-decision model: state + Choice/Score/Noul questions,
typed answers with probabilities, ~100-500 ms, $0.042/M input tokens, no text generation), grouped by the kind of
software capability it enables. Sources: yibie/awesome-jev (~190 entries), walidboulanouar/awesome-jev-use-cases
(74 demos, 148 repos), logicrw/awesome-jev-projects (287 -> 420 commit-pinned projects), ayautomate.com/jev-builds
(1,305 builds), the r/LLMDevs "I reviewed 287 open-source Jev projects" post, TypeSafe cookbooks. Compiled 2026-09-21.
All numbers are the builders' own claims unless tagged [measured]; nobody has replicated TypeSafe's 193.6x/444.6x.

## Contents
- Semantic conditions in ordinary code
- Judge everything, all the time
- Real-time loops
- Agent and harness decisions (incl. Jev Router)
- Verify every step of another AI
- Generate with an LLM, judge with Jev
- Search and retrieval without an index
- Matching and deduplication
- Triage that shrinks a human queue (incl. model routers, cascades)
- Features for classical ML
- Games, simulations, control
- Plain-language personalisation
- Architectural tricks that recur
- Where it fell short
- Not shipped yet

## Semantic conditions in ordinary code

A predicate written in English runs where a regex, SQL WHERE, or `if` would run: no embeddings, no index, no
training. With LLMs this meant one slow call per row and JSON parsing; with Jev it is one Noul per row batch,
~200 ms, thousandths of a cent, cached on repeat.
Shape: one Noul (or Choice/Score) per row/line/element; state = the item text, batch of 16-30; predicate in
instructions; code thresholds, caches, orders, and treats near-equal scores as ties.
- jev() for PostgreSQL (@iam_zachi): `WHERE jev(people, 'could work from home')`; 129 rows in ~1 s for $0.0009,
  6 ms cached [claim, walid]. Repos: pg-jev, pg_typesafe (C), jevql (no extension), sqlite-jev, duckdb-jev,
  mysql-ailike, polar_llama (Polars typed columns) [awesome-jev, logicrw].
- duckdb-jev (prasanthj): 1,943 rows/s for 1,000 Choice classifications [awesome-jev]; @hamiltonulmer's DuckDB
  extension: ~10 s per 1,000 rows [claim, awesome-jev].
- kyu1204/jgrep: one Noul per 5-60 line code chunk, diff hunk or CSV row, 16 per request; 896-chunk TS `src/`
  in 1.8 s for $0.010, repeat 0 s cached; "English sentences work as CI lint rules" [measured by author, logicrw].
- keltokhy/jgrep: "grep, but the pattern is a description", ~200 ms and a thousandth of a cent per line [claim, walid].
- uehaj/jev-semgrep: scores every line against a meaning, AND/OR/NOT, cross-language (Japanese query finds English
  code), ~30 lines per batch [awesome-jev]. sufianetaouil/every: yes/no question of every function in a repo [logicrw].
- carldaws/hunch (Ruby): `if Hunch.likely?("fraudulent", given: order)`; jomatsu/zod-jev: semantic rules inside Zod
  validation ("matches this description", "contains PII") [awesome-jev, logicrw].
- yusukebe/hono-jev-router: HTTP requests routed by the meaning of a route description [awesome-jev];
  Vicente-MD/jev-resilience: detects error messages hidden in HTTP 200 bodies (Spring WebFlux) [logicrw].
- HA-Jev: Home Assistant sensors from questions like "has finished laundry been left unattended?" [awesome-jev].
Watch out: jev-orderby-bench: ORDER BY over a Jev probability passes on 20 Newsgroups but fails 4/6 conditions on
Amazon ESCI, and 40-row batching fails a gate that one row per request passes [awesome-jev]. jevkit grep: 33 %
recall at threshold 0.5, batch-of-8 ranks are "coarse" [measured, jevkit]. Unrelated rows in one state lower accuracy.

## Judge everything, all the time

Ask the same 5-60 questions of every item in a corpus (1,000-10,000 items) in seconds for cents, then aggregate
into a column, dashboard, heatmap, or audit. With LLMs this cost dollars and hours; with Jev $0.08 and 256 ms/item.
Shape: fixed question pack per item (Choice + several Nouls/Scores); state = one item (often an LLM summary or
OCR text produced once); parallel batches; code aggregates, charts, links top items for manual check.
- 1kpapers (@nutlope): 1,018 papers, DeepSeek summaries $3.99 then Jev Choice over 24 topics $0.08, 256 ms median
  per paper [claim, walid, ayautomate].
- 3,282 X posts x 8 questions for $0.1282 (@iannuttall); Every's editorial check: 21 questions x 37 docs = 1,709
  judgments under $0.01 (@danshipper) [claim, walid].
- 384 news stories -> which 15 brands should react, 24.9 s, $0.19; Opus 5 got through 4/384 for $0.77 (@elvissun;
  ayautomate flags "unsupported claim") [claim, ayautomate].
- 724 competitor ads broken down (@TheMattBerman); 700 leads scored in 40 s (@romanbuildsaas); 900 OCR'd images
  sorted in 40 s (@fayazara) [claim, walid].
- BTK SEO audits: 1,204 pages per run, 4,816 judgments in < 3 min, $0.0048 per 12-query batch [awesome-jev];
  jev-linkmap: 566 pages, 8,460 internal-link decisions in one run [logicrw].
- elvex harness: 2,000 expense reports categorized in 20 s for $0.05 [awesome-jev].
- Jevtown: 10,000 personas react to a draft; ~60 Scores + 7 moderation Nouls, then Choice waves of 600/1,500/3,000
  [awesome-jev]. jjd-lab: Jev and GPT-4.1 as the same 300 survey respondents over 24,596 cells at 1/34 the cost.
Watch out: AI-decision-maker measured Jev at 6.6-12.7x an LLM's token cost on CSV column typing because
per-question criteria repeat while output is one character [measured, awesome-jev]. Bryo AI reports conflict (10-20x cheaper per
TechCrunch, 10-20x more expensive per ayautomate); do not cite [ayautomate, techcrunch].
not made the vault faster or proven better research" [ayautomate].

## Real-time loops

Judgment that re-runs on every keystroke, scroll, partial transcript, frame, block, or token window, so the product
reacts while the user is still acting. LLM round trips of 1-5 s made "as you type" impossible; Jev re-asks 16-61
questions per event for free output tokens.
Shape: fixed pack of Nouls/Scores re-asked over the current buffer (debounced), or one Choice per tick over legal
actions; code keeps the previous answer while a new one is in flight and applies hysteresis.
- TypeSafe Typewriter (@stevekrouse): 16 judgments re-asked on each keystroke [walid]. Keystroke oracle predictive
  launcher and Predictive spreadsheets (~100 ms per cell) (@dabit3) [claim, walid].
- Post scoring with SuperX (@robj3d3): 61 questions about a draft in ~1 s; Live viral post analyzer: score 0.5 s
  after you stop typing (@rileybrown) [claim, walid].
- Real-time slop detector as you scroll (@RBilgil, 685 followers, 7,180 likes); linkedin-slop-blocker: free
  pattern scan first, then one Jev call per scroll [walid].
- jev-canvas (gaborishka): on every partial voice transcript 8 typed questions (is it a command, complete, action,
  shape, colour, target, place, size), code gates by threshold, EN + UK, 300-550 ms per decision [awesome-jev].
- Always-on assistant with no wake word (@_MaxBlade): command for the computer vs ordinary talk [walid];
  jev-voice-browser: intent + target per partial transcript, judges completeness and sensitive actions [logicrw];
  aiavatarkit: turn-ending judgment; slidepilot: auto-advance slides when the topic is covered [logicrw].
- jev-model-tokengate: proxy scores each sliding window of tokens while the LLM streams and cuts the stream before
  a violating token reaches the screen [logicrw].
- jev-trader (@jarrodwatts): buy/sell decision every 300 ms Monad block, real post-only orders [claim, walid].
Watch out: memory-relevance check was 708 vs 5,690 ms median but the fallback route cost 27 % more than the LLM
alone [claim, ayautomate]. Routers flap between tiers on near-identical inputs; huncho ships enter/exit hysteresis
for this [walid, awesome-jev]. Extension fetches must go through the service worker (page CSP blocks localhost).

## Agent and harness decisions

Every step of a browser, desktop, mobile, robot, or tool-calling agent becomes a bounded Choice over candidates that
code enumerated (DOM elements, accessibility controls, OCR regions, MCP tools), and a generative model is called
only to type text; plus context GC that keeps survivors verbatim instead of summarizing. Frontier-model steps cost
seconds and cents each; Jev steps cost ~$0.0002-0.001 and 100-400 ms.
Shape: state = pruned DOM/accessibility table with numbered elements + goal; Choice over (operation, target), Nouls
"goal reached", "stuck", "irreversible", "needs text"; code validates the pick exists and sums to 1, executes,
rebuilds candidates every step; catalogs > 255 options go hierarchical.
- browser-use/jev-ultrafast (7,798 stars): Jev picks action + element, small LLM only to type; flight search in
  7 s for $0.0039 [claim, walid]. Ports add goal-reached/stuck Nouls (jev-for-chrome), ~300 ms/step (jev-ra) [logicrw].
- Computer use without screenshots (@milindlabs): on-device OCR/segmentation to text, Jev drives the pointer;
  awlevin/typesafe-computer-use: ~$0.0002 per step [claim, walid]. Yappy: one Choice per step over the front
  window's accessibility table, 275-690 ms, escalates to an LLM agent on low confidence or no-effect actions.
- droidrun/mobile-jev: Uber route entered in ~21 s for 9 actions [claim, walid]; Stagehand + Jev: ~$0.001 per task;
  WebMCP author: Jev + small LLM solved 100 % of tasks at ~112x lower model cost [claim, awesome-jev].
- json-render (Vercel Labs): Jev picks components and props, code assembles the UI; 3.21 s -> 0.88 s [reddit-287].
- A chat bot with no LLM (@CodingGarden): Jev chooses tool and arguments [walid]; jev-mcp-dispatcher picks the MCP
  tool and extracts arguments from the sentence; TypeSafe skill-suggestion cookbook: at most one of 182 skills.
- Jev Router (TypeSafe, `typesafe/jev-router` on OpenRouter, listed 2026-09-25): an off-the-shelf LLM router on
  the chat-completions endpoint (takes `messages`, `tools`, `reasoning_effort`); Jev picks the model and reasoning
  effort per request, and the cost is the routed model's, reported in `usage.cost`. As of 2026-10-01 the routed-model
  list and any quality benchmark were unpublished. It is the one way Jev ends up in an agent's model slot. For "which
  model answers", compare three arms on your own traffic: Jev Router, a self-built Choice over models with
  hysteresis (the community model routers under "Triage that shrinks a human queue"), and a fixed model.
- Context GC: fast-jev-compaction (4,031 stars, most-liked demo at 10,435 likes) keeps/truncates/drops each tool
  call verbatim; jev-pruner trims Bash output before the model sees it; Winnow, yoshi, 25 ports [walid, logicrw].
  jev-use: p50 ~230 ms, ~$0.02 per 1,000 judgments [measured by author, logicrw]. jev-mode: 78 % fewer tokens,
  accuracy 96.1 vs 93.7 % on triage/tagging/routing [own A/B, logicrw]. wakegate: skip waking a sleeping agent only
  when wake < 0.2, 21/21 scenarios ("smoke test") [awesome-jev]. hippo-memory reranker: R@1 0.41 -> 0.62.
Watch out: Theo: "a terrible compaction strategy; compaction is reconstruction, not filtering" [awesome-jev].
jevkit build-log compactor: 58 % recall alone, 100 % only with error pinning [measured, jevkit]. browser-use executes
nothing on a malformed answer; Jev-Auto-Router needed independent verification that routed tasks still passed.

## Verify every step of another AI

A cheap independent referee inside the loop: is this tool call destructive or off-task, is this "done" claim
supported by the diff and tests, does the commit message match, is this install script exfiltrating, must this
message be blocked; and as an online eval judge with near-zero variance. An LLM reviewer per step doubled latency
and cost; Jev is ~400 ms and 8.7x faster than the approval flow it replaced.
Shape: one request with 4-14 Nouls + a risk Score (+ Choice allow/ask/deny) over the proposed action, recent context
and the user's request; deterministic rules settle clear cases first; protected paths always ask; errors deny
(safety gates) or fail open (advisory hooks) by explicit design.
- PR review in one call (@redp314): 14 typed checks (secret, SQLi, touches auth, deletes tests, description matches
  diff...), code -> BLOCK/review/nits/merge, 0.35-0.65 escalates; $0.00007 per PR vs ~$14.50 per 1,000 on Opus 5
  [claim, ayautomate].
- jev-axi: shell commands scored for destructiveness/exfiltration/RCE, routine ones decided locally, 44/44 on its
  labeled calls; hermes-jev-approvals: 8.7x faster, 4.4x fewer prompts on 153 real commands [awesome-jev].
- Reflex: 5 Nouls + risk Score per state-changing call, ~400 ms; pi-verdict: Choice allow/ask/deny only for the
  grey zone, timeouts deny; jev-engineering publishes a 300-call injection test of what walks past [awesome-jev].
- Completion claims: Foreman (Nouls stuck/off-track/verify over worker diffs and tests), limpet, jev-belay (one
  4-question call only when files changed with no passing check), Canny (execution ledger) [awesome-jev, reddit-287].
- mastra-jev-moderation: "must block?" + category Choice, aborts at 0.7, fails open behind a deadline; production
  9/9 hostile blocked, 0/49 real blocked, ~0.4 s, ~4x cheaper than an LLM moderator [awesome-jev]. Vercel engineer:
  replaced an OpenAI safety classifier, 5-18x faster [claim, ayautomate].
- LangChain judge eval: 100 % oracle agreement (Terra 99.8, Luna 96.4, Claude 80.0), variance 1.49e-5, 0.44 s,
  $0.34 per 1,000 vs $28.17 for Claude; "a narrow test" [measured, langchain]. jevcal fits thresholds to a target
  accuracy and fails CI on drift; jev-ood-calibration: Choice/Score overconfident, Boolean underconfident.
Watch out: Abide: reviewer confirmed only 10 of 39 flagged edits and 11 of 15 flagged turns [awesome-jev]. Injection
detection 87.0 % vs Haiku 4.5 89.0 % [measured, ayautomate]. Attacker-controlled text can steer the answer; a
consistently wrong cheap judge scales its mistakes [langchain]. Fail-open only for reversible enhancement layers.

## Generate with an LLM, judge with Jev

Split the work: the generative model writes (summary, rewrite, story, code, prose), Jev scores it against a fixed
rubric of 8-61 atomic questions cheaply enough to run on every draft, paragraph, file, or PR, and stably enough to
gate CI. LLM rubric scoring drifted, varied run to run, and cost too much per unit.
Shape: many Nouls/Scores over one unit in one request; rubric levels describe concrete situations and carry observed
numbers; weights, arithmetic, verdict labels, and "rewrite then re-score" loops live in code.
- 1kpapers: summaries $3.99, judging $0.08, so judging 1,018 papers cost ~50x less than writing [claim, walid];
  will-it-hit: 8 Scores + 1 Choice per draft, an LLM rewrites, Jev re-scores the rewrite [walid].
- Sniff Test: 10 Nouls per paragraph at 0.7, 182 ms median, 1 of 54 clean paragraphs flagged vs 37 for Haiku 4.5
  [awesome-jev]. slopcheck-jev: regex settles 18 tells, Jev 15 in one call, 604 ms; deleting a second
  "pin the sentence" call raised precision 0.80 -> 0.95 [own measurement, logicrw].
- Clean Code Judge: 31 Boolean smells per PR file, verdicts handed to a writing model; Supercov: 12 Nouls per source
  file so the agent knows what to fix first; jev-review (326 stars) staged review dashboard [awesome-jev].
- jev-resume-screening: 5 Noul evidence gates + 4 Scores + 1 Choice per resume; hardened v1->v3 until a glossy-trap
  "AI heavy user" fell 0.95 -> 0.49 [awesome-jev]. killmyidea: Scores -> KILL/FIX/SHIP in code [reddit-287].
- Live BS meter on a debate (@chetaslua): every sentence, 5 Nouls each, 1,191 calls, 415 ms median, $0.0497
  [claim, ayautomate]. jev-got: LLM writes a text adventure, Jev labels beat, mood, danger [logicrw].
Watch out: 12-14 Jev-scored dimensions with fitted weights beat one judge question (0.9076 vs 0.8373) but flagged
~25x more benign rows as attacks [awesome-jev]. Noul and yes/no Choice on the same thing return different numbers;
don't interpolate between Score levels; Spanish state costs 3.0-6.4 pp [awesome-jev].

## Search and retrieval without an index

Rerank a shortlist, select evidence within a token budget, find the file or graph edge most likely to lead to the
answer, narrow an icon set by phrase, or extract a span by choosing among numbered candidates, with nothing
indexed and no embeddings. Cross-encoders needed training; LLM reranking cost too much per query.
Shape: state = query + up to ~30 candidates; one Noul/Score per candidate; for graphs one Choice over outgoing
edges + goal Noul with beam search in code; for extraction the options are candidate spans/ids so the output is
provably a substring or catalog item.
- TypeSafe rerank cookbook: 40 legal queries, top-1 5 % -> 18 %, top-10 38 % -> 62 % [cookbook]; llama-index-jev:
  nfcorpus nDCG@5 0.340 -> 0.396 at ~$0.0003/query, "first-stage retriever is weak" [awesome-jev].
- jselect: evidence within a token budget via Noul relevance + local diversity; jevrag: five calibrated RAG decision
  points (stop retrieving, split chunk, select context, abstain, trust cache) [awesome-jev, logicrw].
- Blink (ellipsis): walkers through the directory tree distributed by Jev's file/dir scores [reddit-287]; jev-assist:
  ranks every file in a 600-file repo for a task, validated against past commits [awesome-jev].
- neo4jev: at each node a Choice over relationships + goal Noul, beam search [reddit-287]; jev-bfs: Wikipedia link
  race [awesome-jev]. jev-search (199 stars): Jev picks sources, time ranges, terms, then ranks results [walid].
- Extraction by selection: jeveryword numbers the words and returns the picked substring with offsets; cookbooks
  for pre-parsed values (regex finds candidates, Jev picks), date parts, Markdown structure recovery in two requests,
  SDE cascade; jev-pii-checker: 12 category Nouls + sensitivity Score, spans via regex [logicrw, cookbook].
Watch out: over 33,047 catalog entries, 164 real queries and 9,831 graded pairs, Jev reranking alone did not beat
vector retrieval [awesome-jev]. ORDER BY fails 4/6 gates on ESCI product relevance. Jev cannot return free text, so
anything not offered as an option is unreachable.

## Matching and deduplication

Decide whether two records, an item and a criterion, or a candidate and a slot refer to the same thing or fit, under
a plain-English match rule, with code doing candidate blocking. String similarity misses semantics; pairwise LLM
calls over blocked candidates were too expensive.
Shape: state = both records (a duplicate check needs both in state) or item + criteria; Noul "same entity / fits"
or Choice duplicate / related / distinct / insufficient; code generates candidate pairs and resolves accepted matches.
- keltokhy/jlink: record linkage under a user-supplied match definition; exact matching after normalization scored
  0.26/0.41/0.00/0.00/0.22 on its five sets vs Jaro-Winkler/TF-IDF baselines [logicrw].
- TypeSafe entity-alignment cookbook: 450 candidate pairs from two beer catalogues; one Score with levels merge /
  leave unlinked / hand to a curator [cookbook].
- jev-issue-radar: GitHub duplicate triage, Choice duplicate/related/distinct/insufficiently documented per pair,
  read-only, lexical retrieval bounded to recent items [logicrw]; typeful-triage asks "duplicate?" per issue.
- 400 companies matched to one candidate for $0.0005 (@sarvagya_kul) [claim, walid]; hearth-jev-rental-search:
  which listings match the criteria across sources [awesome-jev]; JevScout: careers pages screened for role fit.
- jev-scout: repo/crate candidates scored for fit and maintenance signals [awesome-jev]; azdaja: "judge whether
  records match for semantic joins" inside an RLM layer [logicrw].
Watch out: a CRM hygiene sweep is still an unshipped idea; the walid list warns a duplicate check needs both records
in the state, which limits batch size. jev-issue-radar states its retrieval is lexical and bounded.

## Triage that shrinks a human queue

Every inbound email, ticket, log line, issue, PR, prompt or request gets a department, urgency, tier or model in a
few hundred ms, and the confidence decides whether Jev's answer stands, a bigger model is called, or a human sees
it. Cascades reach frontier accuracy at about a quarter of frontier cost.
Shape: Choice over departments/tiers (+ "none"), Score urgency, Nouls for special cases; regex/allowlists first;
read the Choice confidence; below threshold escalate; humans only see the leftovers plus an audit sample.
- Fraud detection (@nutlope): 100 emails in 1.42 s, 31 under 95 % confidence sent to Kimi K3, 96/100 correct, ~$0.07
  [claim, ayautomate]. 500 emails for $0.035 (@rileybrown); 1,500-email triage (@ryanvogel) [claim, walid].
- ayautomate cascade: Jev at >= 0.80 else GPT-5.6 Terra: 90.0 % accuracy at 26 % of Terra's cost, 0.70 vs 1.58 s
  (8-way); confidence >= 0.90 alone lifts 83.8 -> 95.5 % while answering 70 % of items [measured, ayautomate].
- Model routers: gargpratyush/jev-router (191 stars; failures keep the current model), LiteLLM complexity router
  with an anti-injection rule, tiershift ~180 ms, jcm-router (routes subagents, leaves the cached main chat alone),
  opencode-jev-orchestrator (sticky cheap parent) [walid, logicrw, dev.to].
- jev-logtriage: collapsed Loki logs in one call of Noul+Score+Choice mapped to suppress/watch/review/notify/page,
  low confidence -> review, nothing executed [awesome-jev]. secondlayer: Slack gate + fault triage.
- triage-bot: Jev routes to general/account/billing/technical + "should a human take it", Cerebras drafts the
  reply, both timed separately [walid]; typeful-triage: kind/severity/urgency/duplicate/next step per issue, human
  corrections shown back on later runs [awesome-jev].
- DocJev (LlamaIndex): document vs natural-language category rules, 40/40 in a pilot at ~182 ms p50; Notra:
  production classifiers at 0.5 targeting 300 ms p50 [awesome-jev].
- Replacing an agentic taxonomy loop: mean 9.62 -> 1.38 s, calls 7.22 -> 3.18, 36/50 identical, 12 divergent
  (5 to Jev, 4 to the agent), one annotator, no ground truth [measured, r6i].
Watch out: ayautomate benchmark: 83.8/78.8/87.0 % vs Terra 89.4/84.0/86.8, "a good small model, not a frontier
model", confident errors on overlapping labels [measured]. ASSAY-001 on Banking77/CLINC150: split verdict.
"Applying someone else's thresholds (0.65 varies by domain)" is a named anti-pattern [dev.to].

## Features for classical ML

Turn free text into calibrated numeric columns (one per atomic question) that a regressor, a Bradley-Terry fit,
a threshold search, or a human labeler consumes; use the model's errors to propose new questions. Feature
engineering over text used to need embeddings or hand rules; here each feature is a named, inspectable probability.
Shape: a pack of Nouls/Scores per row -> feature matrix; local code fits weights, thresholds, scales, ECE; loop:
propose questions, score rows, train, inspect residuals, repeat.
- TypeSafe autoresearch feature-discovery cookbook: a loop that proposes questions, turns text into numeric
  features, and uses model errors to improve a supervised CatBoost regressor [cookbook].
- agentjournal.dev: 12-14 Jev-scored dimensions with locally fitted weights vs one direct question on three
  classification tasks: 0.9076 vs 0.8373 on Japanese NLI, at the cost of ~25x more benign rows flagged [awesome-jev].
- keltokhy/jsort: pairwise Nouls + locally fitted Bradley-Terry scale with standard errors [awesome-jev].
- sutro-sh/jev-align: score rows, send ambiguous + audit samples to a human, use accepted labels to optimize the
  question definition with GEPA; jev-curate and hfjev label rows in bulk for training sets [awesome-jev, logicrw].
- jevcal: fit a per-question confidence threshold to a target accuracy on your labels, verify held-out, report
  escalation share, fail CI on drift; huncho: replay a threshold change over recorded answers with no inference.
- Luce: an LLM teacher writes training data from a one-sentence task, a LoRA + decision head answers with
  calibrated probabilities; beats Jev on identical items (91.1 vs 75.1 rule tickets, 97.4 vs 62.6 phishing).
Watch out: Choice and Score are overconfident, Boolean underconfident [jev-ood-calibration]; asking a yes/no item as
Noul vs Choice moved a survey result more than the model gap [jjd-lab]. Log state, probabilities, model version and
outcome or you cannot recalibrate later [dev.to].

## Games, simulations, control

An agent that acts every tick (2.5 Hz to ~1 s/move) from structured state, choosing among legal moves that code
enumerated, with the distribution visible and calibratable; the same shape drives robot arms, drones, and trading
loops. Token generation cannot keep up with Subway Surfers; a frontier model at 20 s/move loses to the clock.
Shape: one Choice over legal actions (illegal moves excluded by construction), sometimes several Choices + a Noul
in one call; state = emulator RAM, JSON scene, sensor sectors, order-book features; code owns physics, geometry,
pathing, arithmetic, position limits; Jev "picks only at branches".
- Jev plays Doom (TypeSafe founder, 4,890 likes), Subway Surfers, Smash Bros vs itself, Super Mario Bros from
  emulator telemetry (278 stars), Slay the Spire 2 at 0.7 s/move [claim, walid].
- Rubik's cube (@redp314): beginner method in code, Jev picks which case the cube is in, code checks every pick;
  94 moves, ~250 ms per question, ~4 s model time total [claim, ayautomate].
- jev-drone: camera-only quadrotor in MuJoCo at ~2.5 Hz, classical control keeps stability [walid, reddit-287];
  RoboJEV: intent Choice then X/Y/Z + gripper Choice for a Franka Panda, physics checks success [awesome-jev].
- Jev Chess: every legal move is a Choice option, probabilities shade the board, live calibration panel against a
  one-ply material check [awesome-jev]; jev-plays-pokemon-red: code owns route and arithmetic.
- City junctions (Markus Hjort): ~350 ms per request, ~$0.001 per minute of traffic, "behavior is chaotic"
  [claim, ayautomate]. jev-torneo-animales: 1,999 fights in ~16 s for ~$0.01 via speculative champion-vs-K batching.
- Trading: jev-trader (1,184 stars) decides every 300 ms block on Kuru; $10,000 handed to Jev (@abolbuild);
  jev-trade on Hyperliquid; Prism keeps execution deterministic and Jev advisory [walid, awesome-jev, reddit-287].
Watch out: no source reports trading P&L; "I wouldn't treat this as evidence that Jev has alpha" [reddit-287].
Jev has no lookahead (jev-demos maze, poker "fish at the table"); Jev is not a calculator, so counting, dates and
geometry stay in code [walid].

## Plain-language personalisation

The end user writes the rule ("hide engagement bait", "file screenshots to /Design", "show only questions in this
chat") and the software enforces it per item in real time with a visible probability. Per-item LLM calls were too
slow and expensive to be always-on; rules engines cannot read meaning.
Shape: state = one item (post, DOM element, filename + metadata, chat line); instructions = the user's rule; Noul
per rule or one Choice over user-defined categories; code folds/hides/tags/moves, keeps it reversible, learns
from what the user dismisses.
- Hide posts on X in plain language and A Downloads folder that sorts itself, "Jev as the only LLM"
  (@marcelpociot, ~1,090 likes each) [walid].
- Doomscroll Filter (@robj3d3): pick a niche, posts become Read/Skim/Pass; sift labels every X post
  Substance/Humor/Promo/Junk/AI-written; your-signal weights relevance/substance/promotion [walid, logicrw].
- Jev tagger (walid maintainer): user writes categories with a plain-English description and colour, one Choice per
  post while scrolling, low confidence stays untagged, each category shown/dimmed/hidden [walid].
- Real-time ad blocker (@iam_zachi, 3,872 likes) and unclutter (129 stars): per-DOM-element Noul, reusable rules.
- Jev Chat for Twitch: one Choice per message in batches of 20, ~$0.15/h at 2 msg/s, $0.76/h at 50 msg/s;
  PlotVeil: spoiler Noul per YouTube comment at 0.85/0.7/0.5 [awesome-jev].
- jev-skip: caption segments -> content/sponsor/intro/outro/self_promo/recap, painted on the seek bar; 77 % of
  SponsorBlock's sponsor seconds over 23 videos at $0.0008 a video [awesome-jev].
- Website visitor routing: ask "what are you trying to do?" and send the visitor to the right docs or pricing
  page, a Choice over the site's pages [claim, Medium "6 product ideas"].
Watch out: adversarial text (chat spam, fake reviews, job scams) is the weakest input; selectors on LinkedIn/X change
on every deploy; the icon-set demo has a thread on what Jev gets wrong [walid, awesome-jev].

## Architectural tricks that recur

- Perception to text first: OCR, accessibility tree, pruned DOM table, emulator RAM, captions; input is text, 32k cap.
- Code enumerates the candidates, Jev only picks; always include a "none applies" option; validate the answer
  (option exists, keys match, sums to 1) and execute nothing on malformed output [dev.to, browser-use].
- LLM only for prose or typing; Jev for every decision; generate once, judge many times (1kpapers 50x split).
- Many questions per call: 13 questions in one request was 12.2x cheaper and 10x faster than one call each
  [cookbook]; ask independent atomic questions and compose with weights in code.
- Many items per state (`posts[0]`, 16-30 per batch) cuts cost but lowers accuracy and ranking quality; keep
  batches small and check by hand.
- Deterministic rules first, Jev second, human third: regex settles secrets and OTPs with no call at all.
- Confidence-gated cascade: answer when sure, escalate the band (0.35-0.65, < 0.80, < 0.95) to a big model or human;
  fit the threshold on your own labels (jevcal) and report escalation share.
- Fail-open vs fail-closed by reversibility: gates on deletions and payments deny on timeout; advisory hooks and
  moderation behind deadlines fail open; ship shadow mode first (jev-skill-router, Prism).
- Human overrides no probability can bypass: protected paths always ask, high risk forces authorisation.
- Keep survivors verbatim and return offsets (compaction, jeveryword, jev-reviewer); never let Jev rewrite.
- Cache by content (jev() 6 ms on rerun, jgrep 0 s), add hysteresis and sticky routing to stop flapping.
- Hierarchical Choice for catalogs over 255 options (Blender, jev-tree, beam search); anchor rubric levels to real
  outcomes and harden them against negative controls; log state, probabilities, model version and outcome.

## Where it fell short

- Reranking: over 33,047 entries, 164 queries, 9,831 graded pairs, Jev alone did not beat vector retrieval [GoSailGlobal].
- ORDER BY on a Jev probability fails 4/6 pre-registered gates on Amazon ESCI; 40-row batching fails what 1 row passes.
- Memory relevance: 708 vs 5,690 ms median, 78/81 correct, but the fallback route cost 27 % more [Hugo Sequier].
- CSV column typing: 6.6-12.7x an LLM's token cost because criteria repeat per question [AI-decision-maker, measured].
- Intent routing: 83.8/78.8/87.0 % vs GPT-5.6 Terra 89.4/84.0/86.8; 3.6x faster and 40-49x cheaper, not 193.6x/444.6x
  [ayautomate, measured, 3,955 calls]; injection 87.0 % vs Haiku 4.5 89.0 %.
- jevkit (the list maintainer's own tool): grep 33 % recall at 0.5, log compactor 58 % recall without error pinning.
- Spanish state costs 3.0-6.4 pp accuracy and roughly doubles ECE on XNLI/PAWS-X [jev-acento, 3,200 items].
- Supervision precision: Abide's independent reviewer confirmed 10 of 39 flagged edits and 11 of 15 turns.
- Specialists win at home: CUA-S1-FORMS 99.7 % vs Jev 83.6 % on forms; Luce 91.1 vs 75.1 and 97.4 vs 62.6 on its items.
- Theo on compaction: "a terrible compaction strategy", compaction is reconstruction rather than filtering.
- Bryo AI: the ayautomate index records "slightly more accurate but 10 to 20 times more expensive" than Gemini on
  email classification, while TechCrunch quotes the same company as 10-20x cheaper; conflicting, do not cite.
- Calibration is not uniform: Choice/Score overconfident, Boolean underconfident; ASSAY-001 split verdict; a yes/no
  asked as Noul vs Choice shifts results more than switching models [jjd-lab].

## Not shipped yet

From walidboulanouar/awesome-jev-use-cases (brainstorm 2026-09-19), with status as of the logicrw index:
- A tone meter attached to any text box (Gmail, Slack, X) — not seen; TypeSafe Typewriter is a dedicated editor.
- Live chat moderation with Nouls for toxicity/spam — since appeared (Jev Chat for Twitch, Jev Moderation Bot).
- A feed reranker that asks the user a question only when confidence is low — not seen.
- A model router scoring prompt complexity before the call — since appeared (34 routers in logicrw).
- CI test selection from a commit diff — since appeared (baronunread/leanest runs everything on uncertainty).
- Abuse scoring at an API gateway (rates in code, attacker-controlled text) — since appeared (traffic-guard).
- Job board scam filter (real / ghost / scam per card) — partly (JevScout screens roles, not scams).
- Marketplace price-trap detector with prices compared in code — not seen.
- Fake review flagger as the list loads — not seen; text alone is a weak signal.
- Support ticket triage: Choice department, Score urgency, Noul refund — since appeared (triage-bot, jev-demo).
- Inbound lead scoring on form submit, calibrated on closed-won/lost — not seen (700-lead demo is batch scoring).
- Outbound message compliance check, one Noul per policy rule before send — nearest is jev-oas-sentinel for specs.
- CRM hygiene sweep for record quality and duplicates — not seen.
- Elsewhere: Cua asks "what the next specialist should learn" after forms; Ask HN proposes Noul as a general software
  primitive; milindlabs "voice mode next if people want it"; jev-issue-radar deliberately never writes; awesome-jev's
  Scientific Pipelines category is still empty despite jev-reviewer and paper-radar-jev existing.
