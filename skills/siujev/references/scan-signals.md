# Scan signals: finding Jev candidates in a codebase or design

Use this when the ask is "where could Jev fit?" rather than "is this one
decision a fit?". The goal of the scan is a short list of decision points, each
described in one line with its decision shape, before any fit check.

The scan has two passes. The **replacement pass** finds judgments the
software already makes badly or expensively. The **opportunity pass** finds
judgments the software does not make at all because, until now, a judgment
cost seconds and cents; at 100–500 ms and hundredths of a cent per call, a
judgment can sit inside a loop, a query, a keystroke handler, or a rule a user
writes in plain language. The second pass is where Jev pays off most, and it
is the one an agent skips unless told to do it. Do both, and keep the two
lists separate in the report.

## Replacement pass: what a candidate looks like

A candidate is a place where the program needs a **judgment about unstructured
text** and then **branches, sorts, filters, scores, or routes** on it. Three
families:

1. **Judgments written as brittle code.** Keyword lists, regexes standing in
   for meaning, hand-weighted scoring functions, giant `switch` statements over
   free text, "TODO handle synonyms".
2. **Judgments already delegated to an LLM whose output is a label.** Prompts
   that end with "answer with one word", "return JSON with a category and a
   score", "respond yes or no"; JSON-mode calls whose schema is an enum or
   boolean; `temperature=0` classification calls; logprob tricks.
3. **Judgments made by people that could be triaged.** Review queues,
   moderation, ticket assignment, lead qualification, resume screening,
   deduplication, where a first pass with calibrated confidence would let
   humans see only the uncertain cases.

## Grep-able patterns (adapt to the language)

Search the code, config, and prompts for:

- Text-matching heuristics: `.includes(`, `in text`, `re.search`, `preg_match`,
  `strpos`, `matches(`, `keywords = [`, `STOPWORDS`, `synonyms`, `blacklist`,
  `whitelist`, `fuzzy`, `levenshtein`, `similarity >`.
- LLM-as-classifier: `classify`, `categor`, `intent`, `sentiment`, `is_spam`,
  `is_urgent`, `severity`, `priority`, `route`, `triage`, `moderat`, `toxic`,
  `label`, `tag`, `score`, `rank`, `rerank`, `relevan`, `dedup`, `match`,
  together with an LLM client import (`openai`, `anthropic`, `gemini`,
  `langchain`, `litellm`, `ollama`) or prompt files containing "respond with",
  "answer only", "one of the following", "JSON", "yes or no".
- Verification of AI output: `hallucinat`, `guardrail`, `jailbreak`,
  `prompt injection`, `citation`, `groundedness`, `validate_response`,
  `judge`, `eval`.
- Retrieval: `embedding`, `cosine`, `vector`, `top_k`, `bm25`, `rerank`,
  `rrf`; the reranking step and the "is this chunk actually relevant" filter
  are candidates, the embedding index itself is not.
- Human queues: `needs_review`, `manual_review`, `assign_to`, `escalat`,
  `pending_approval`, `flagged`.
- Form/field extraction: `extract`, `parse_.*_from_text`, `NER`, `entity`,
  `dateparser`, `address`, `phone`, `amount` applied to free text.

## Opportunity pass: capabilities that become practical

Walk through the software's loops, streams, tables, queues, and user-facing
controls and ask, for each family below, "would a cheap calibrated judgment
here change what the product can do?" `references/use-case-catalog.md` has
named examples with numbers for every family; use it to make the proposal
concrete.

| Family | Trigger question to ask about the software | Typical shape |
|---|---|---|
| **Semantic conditions in ordinary code** | Is there an `if`, `WHERE`, sort key, or filter that today matches keywords but really means something semantic ("looks like a complaint", "could work remotely")? Do users configure rules by keyword lists? | one Noul per condition; user-written rule text goes into `instructions` |
| **Judge everything, all the time** | Is there a table, feed, log, archive, or corpus that nobody scores because scoring each row with an LLM would cost too much? Would a "quality", "risk", "fit", or "topic" column change how people use it? | one request per row, 5–20 questions each; results stored as columns |
| **Real-time loops** | Is there a per-keystroke, per-frame, per-tick, per-message, per-block, or per-transcript-chunk step where a judgment under 500 ms would enable a feature (live feedback while typing, live chat moderation, live control, voice commands, sponsor skipping)? | small state, 1–15 questions, called continuously; code owns the loop and the safety rails |
| **Agent and harness decisions** | Does an agent pick tools, elements, actions, models, skills, memories, or context with an LLM call whose output is a choice? Could code enumerate the candidates so the LLM only writes text when text is needed? | Choice over code-generated candidates + Nouls for "should we act / stop / ask"; LLM only for typing |
| **Verify every step of another AI** | Does the system trust LLM output (extractions, citations, tool calls, replies, generated content) without a check because a second LLM call would double the cost? | one Noul per failure mode per artifact; cascade to a human or a bigger model on flags |
| **Generate with an LLM, judge with Jev** | Is there a rewrite / draft / candidate-generation step whose outputs could be scored and selected, or a loop that would improve if it could score its own attempts? | LLM produces N candidates, Jev scores each on 3–10 Score questions, code picks or iterates |
| **Search and retrieval without an index** | Is there a small-to-medium set (hundreds to low thousands) searched by keyword where users mean something semantic? A shortlist from BM25 or embeddings that needs reranking? A long document where the question is "which line answers this"? | one Noul or Score per candidate; Choice over line ids; `exists` Noul |
| **Matching and deduplication** | Are records, candidates, listings, leads, or entities matched by exact or fuzzy string rules? | one request per pair with both records in state; Noul or 3-level Score (merge / review / distinct) |
| **Triage that shrinks a human queue** | Is there a review queue where most items are fine and reviewers would rather see only the uncertain ones? | decomposed Nouls + confidence bands; measure queue reduction |
| **Features for classical ML** | Is there a predictive model (churn, conversion, demand, risk) that ignores free text because nobody could featurize it? | 10–40 Score/Noul questions per record, stored as numeric features |
| **Games, simulations, control** | Is there a state machine or control loop where "which case are we in" is a judgment over structured state? | Choice over the enumerated cases, code executes and validates every pick |
| **Plain-language personalisation** | Could users describe what they want to see, hide, sort, or be alerted about in a sentence instead of a settings form? | user sentence in `instructions`, item in state, one Noul per rule |

Not every family applies to every product. Pick the two or three that fit the
domain, propose one concrete feature per family with its question sketch, and
run the fit check on it like any other candidate. Label these proposals as
**new capability** in the report so the reader can separate them from
replacements.

## Design documents and issue trackers

When there is no code yet, scan requirements for verbs: classify, detect,
decide, prioritize, route, flag, rank, match, verify, screen, triage, moderate,
extract (a known field), score, assess. Each one over free-text input is a
candidate. Verbs like generate, summarize, draft, explain, translate, plan,
negotiate are not.

## Writing up a candidate

One line each, in this form:

`<where> — <what is judged> — <shape: classification | detection | scoring | routing | ranking | verification | extraction-by-selection | matching | feature-extraction | pre-filter> — <current implementation> — <volume / latency context if known>`

Example:

`support/triage.py:42 — assign incoming ticket to one of 6 teams — classification — GPT prompt returning a JSON label, ~1.8 s — 20k tickets/day, async`

Then run the fit checklist on the shortlist, starting with the highest-volume or
most fragile items. Do not fit-check more than five or six in one pass; the user
can ask for the rest.

## What not to list

- Deterministic parsing that works (CSV, JSON, dates in ISO format, IDs).
- Anything whose output is prose.
- Numeric computations, aggregations, joins.
- Judgments over images/audio unless a text description already exists.
- Places where the "judgment" is really a database lookup.
