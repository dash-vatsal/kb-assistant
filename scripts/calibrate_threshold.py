"""T-041: choose MIN_VECTOR_SIM from data.   python scripts/calibrate_threshold.py eval/questions.yaml
Uses retrieval only (no answer model): best similarity per question, split by answerable vs no_answer."""
import sys
from pathlib import Path
import yaml
from kb.calibration import suggest_threshold
from kb.db import connect
from kb.permissions import user_groups
from kb.retrieval import hybrid_search


def main(path):
    conn = connect()
    pos, neg = [], []
    for q in yaml.safe_load(Path(path).read_text()):
        if q["type"] not in ("answer", "no_answer"):
            continue
        hits = hybrid_search(conn, q["question"], user_groups(conn, q["user"]))
        best = max((h["sim"] for h in hits), default=0.0)
        (pos if q["type"] == "answer" else neg).append(best)
    if not pos or not neg:
        print("Need both 'answer' and 'no_answer' questions.")
        return
    print(f"answerable best-sim: min={min(pos):.2f} median={sorted(pos)[len(pos)//2]:.2f}")
    print(f"no_answer  best-sim: max={max(neg):.2f} median={sorted(neg)[len(neg)//2]:.2f}")
    t, rec, ref = suggest_threshold(pos, neg)
    print(f"Suggested MIN_VECTOR_SIM={t:.2f}  (answers kept {rec:.0%}, off-topic refused {ref:.0%})")
    if min(pos) <= max(neg):
        print("Note: distributions overlap; rely on the model sufficiency check and add more questions.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eval/questions.yaml")
