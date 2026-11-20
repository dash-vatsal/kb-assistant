"""Scoring.   python eval/run_eval.py eval/questions.yaml --judge [--no-rerank] [--vector-only] [--out results.csv]
Metrics: retrieval hit@5, answer correctness (LLM judge), citation accuracy (LLM judge),
correct 'not found' rate, trap pass rate (must be 100%)."""
import argparse
import csv
import json
import re
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from kb import config                       # noqa: E402
from kb.answer import answer_question        # noqa: E402
from kb.llm import generate              # noqa: E402
from kb.db import connect                    # noqa: E402

JUDGE_SYS = ("You grade an internal assistant. Return ONLY JSON: "
             '{"correct": true|false, "citations_supported": true|false}. '
             "correct = the answer agrees with the reference. citations_supported = each claim is backed by the "
             "cited source text provided.")


def judge(q, res):
    srcs = "\n".join(f"[{i}] {h['text'][:1200]}" for i, h in enumerate(res["_hits"], 1))
    msg = (f"Question: {q['question']}\nReference: {q.get('reference', '')}\n"
           f"Assistant answer: {res['answer']}\nSources:\n{srcs}")
    raw = generate(JUDGE_SYS, msg, role="judge", max_tokens=200, json_mode=True)
    return json.loads(re.search(r"\{.*\}", raw, re.S).group(0))


def evaluate(conn, questions: list[dict], use_judge: bool = False) -> list[dict]:
    rows = []
    for q in questions:
        res = answer_question(conn, q["question"], q["user"])
        urls = {h["url"] for h in res["_hits"]}
        blob = res["answer"] + " ".join(h["text"] for h in res["_hits"])
        r = {"id": q["id"], "type": q["type"], "found": res["found"], "answer": res["answer"][:300]}
        if q["type"] == "answer":
            r["hit"] = bool(urls & set(q.get("expected_urls", [])))
            if use_judge and res["found"]:
                j = judge(q, res)
                r["correct"], r["citations_ok"] = j["correct"], j["citations_supported"]
            else:
                r["correct"], r["citations_ok"] = False, False
        elif q["type"] == "no_answer":
            r["not_found_ok"] = not res["found"]
        elif q["type"] == "trap":
            r["trap_pass"] = not any(f in blob for f in q["forbidden"])
        rows.append(r)
    return rows


def metrics(rows: list[dict]) -> dict:
    def rate(key, typ):
        xs = [r[key] for r in rows if r["type"] == typ and key in r]
        return (sum(xs) / len(xs)) if xs else None
    return {"hit@5": rate("hit", "answer"), "correct": rate("correct", "answer"),
            "citations": rate("citations_ok", "answer"), "not_found": rate("not_found_ok", "no_answer"),
            "trap_pass": rate("trap_pass", "trap")}


def fmt(v):
    return "n/a" if v is None else f"{v:.0%}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("questions")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--no-rerank", action="store_true")
    ap.add_argument("--vector-only", action="store_true")
    ap.add_argument("--out", default="eval/results.csv")
    a = ap.parse_args()
    if a.no_rerank:
        config.USE_RERANK = False
    if a.vector_only:
        config.USE_HYBRID = False

    rows = evaluate(connect(), yaml.safe_load(Path(a.questions).read_text()), a.judge)
    m = metrics(rows)
    print(f"config: rerank={config.USE_RERANK} hybrid={config.USE_HYBRID} chunk={config.CHUNK_TARGET_CHARS}")
    print("Retrieval hit@5      :", fmt(m["hit@5"]))
    print("Answer correctness   :", fmt(m["correct"]))
    print("Citation accuracy    :", fmt(m["citations"]))
    print("Correct not-found    :", fmt(m["not_found"]))
    print("Trap pass (must 100%):", fmt(m["trap_pass"]))
    keys = sorted({k for r in rows for k in r})
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("wrote", a.out)
    if m["trap_pass"] is not None and m["trap_pass"] < 1.0:
        sys.exit(2)          # access failures fail the run (usable in CI)


if __name__ == "__main__":
    main()
