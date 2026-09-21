import json, os
from openai import OpenAI

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def chat_json(system: str, user: str) -> dict:
    r = _client.chat.completions.create(
        model="gpt-5-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return json.loads(r.choices[0].message.content)


def draft_reply(ticket_text: str, kb_articles: list[str]) -> str:
    """Generate a first-draft reply for the agent to edit."""
    r = _client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "Draft a polite, concise support reply using only the provided articles."},
            {"role": "user", "content": json.dumps({"ticket": ticket_text, "articles": kb_articles})},
        ],
    )
    return r.choices[0].message.content
