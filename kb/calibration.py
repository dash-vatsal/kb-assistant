"""Pure helper for choosing the not-found similarity threshold."""


def suggest_threshold(pos: list[float], neg: list[float]) -> tuple[float, float, float]:
    """Return (threshold, recall_on_answerable, refusal_rate_on_no_answer) maximising balanced accuracy."""
    cands = sorted(set(pos + neg))
    best = (0.0, -1.0, 0.0, 0.0)
    for t in cands:
        recall = sum(p >= t for p in pos) / len(pos) if pos else 1.0
        refuse = sum(n < t for n in neg) / len(neg) if neg else 1.0
        score = (recall + refuse) / 2
        if score > best[1]:
            best = (t, score, recall, refuse)
    return best[0], best[2], best[3]
