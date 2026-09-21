"""Community forum moderation queue."""
from app.llm import chat_json

BANNED = ["<slur list redacted>"]


def needs_review(post: str) -> bool:
    if any(b in post.lower() for b in BANNED):
        return True
    out = chat_json(
        system="Classify the post. Return JSON {\"harassment\": bool, \"spam\": bool, \"self_harm\": bool}.",
        user=post,
    )
    return any(out.values())


# ~120k posts/day; moderators currently see ~30% of posts, most of them fine.
