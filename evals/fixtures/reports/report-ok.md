# Should I use Jev? — helpdesk triage

Date: 2026-10-01. Facts checked against docs.typesafe.ai on 2026-10-01.

## Summary

Two candidates and one proposal: 1 USE WITH GUARDS, 1 NO, 1 PILOT FIRST. The
team assignment is the most valuable.

## Candidates

| # | Where | Judgment | Shape | Verdict | Why (one line) |
|---|---|---|---|---|---|
| 1 | `app/triage.py:42` | assign ticket to team | classification | USE WITH GUARDS | replaces a 1.8 s LLM call |
| 2 | `app/sla.py:10` | SLA breached | date arithmetic | NO | date logic belongs in code |

## Candidate 1: team assignment

**Decision.** Pick one of six teams for each new ticket; code routes it.

**Verdict: USE WITH GUARDS.**

**Economics.** $0.00002 per ticket, $12 per month (from estimate_cost.py).

## Candidate 2: SLA breach

**Decision.** Whether a ticket breached its SLA.

**Verdict: NO.**

## New capabilities worth a pilot

### Proposal A: live frustration meter

**What the user gets.** Agents see frustration while they type.

**Verdict: PILOT FIRST.**

## Assumptions

- python3 scripts/estimate_cost.py --items-per-day 20000 --state-tokens 600 --questions 3
