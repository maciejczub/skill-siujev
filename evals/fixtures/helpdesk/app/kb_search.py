"""Knowledge-base retrieval for reply drafting."""
import numpy as np
from app.embeddings import embed


def top_k_articles(query: str, articles: list[dict], k: int = 5) -> list[dict]:
    q = embed(query)
    scored = [(float(np.dot(q, a["vector"])), a) for a in articles]
    scored.sort(key=lambda t: -t[0])
    # TODO: many top-5 hits are only lexically similar; agents complain the
    # drafted reply cites irrelevant articles. Consider a reranker.
    return [a for _, a in scored[:k]]
