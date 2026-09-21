"""Ticket triage: assign a team, set a priority, detect refund requests."""
import re
from datetime import datetime, timedelta

from app.llm import chat_json

TEAM_KEYWORDS = {
    "billing": ["invoice", "charged", "refund", "payment", "card", "subscription"],
    "technical": ["error", "500", "crash", "bug", "api", "timeout", "broken"],
    "account": ["password", "login", "2fa", "locked", "email change"],
}

URGENT_WORDS = ["asap", "urgent", "immediately", "outage", "down", "can't process"]


def assign_team(text: str) -> str:
    """Keyword heuristic. Known problems: 'card' matches 'discard', 'api' matches 'rapid'."""
    scores = {team: sum(1 for w in words if w in text.lower()) for team, words in TEAM_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "technical"


def is_urgent(text: str) -> bool:
    return any(w in text.lower() for w in URGENT_WORDS)


def refund_requested(text: str) -> bool:
    return bool(re.search(r"\brefund(ed|s)?\b", text, re.I))


def frustration_score(text: str) -> float:
    """0-2 via LLM; ~1.5 s per ticket, ~$0.002 per ticket at current volume (20k/day)."""
    out = chat_json(
        system="You are a support analyst. Return JSON {\"frustration\": 0|1|2} where 0=calm, 1=frustrated, 2=very angry.",
        user=text,
    )
    return float(out["frustration"])


def sla_breached(created_at: datetime, plan: str) -> bool:
    limit = {"enterprise": 4, "pro": 24, "free": 72}[plan]
    return datetime.utcnow() - created_at > timedelta(hours=limit)


def days_since_last_payment(customer) -> int:
    return (datetime.utcnow().date() - customer.last_payment_date).days
