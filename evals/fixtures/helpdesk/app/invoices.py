"""Supplier invoice intake (accounts payable)."""
from datetime import date
from app.llm import chat_json

PROMPT = open(__file__.replace("app/invoices.py", "prompts/invoice_extract.txt")).read()


def extract_invoice(text: str) -> dict:
    return chat_json(system=PROMPT, user=text)


def is_overdue(inv: dict, today: date) -> bool:
    return date.fromisoformat(inv["due_date"]) < today


def is_duplicate(inv: dict, previous: list[dict]) -> bool:
    """Fuzzy duplicate check; misses reissued invoices with a suffix (-R, /2)."""
    for p in previous:
        if p["vendor_name"].lower() == inv["vendor_name"].lower() and p["invoice_number"] == inv["invoice_number"]:
            return True
    return False
