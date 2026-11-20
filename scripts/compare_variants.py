"""T-052: run the golden set under several configs and print a markdown table for the write-up.
   python scripts/compare_variants.py eval/questions.yaml
Chunk-size variants need re-indexing:  CHUNK_TARGET_CHARS=900 python -m kb.sync confluence ENG --force
then run this script again and note the chunk size in your table."""
import sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.run_eval import evaluate, fmt, metrics   # noqa: E402
from kb import config                               # noqa: E402
from kb.db import connect                           # noqa: E402

VARIANTS = [("baseline (hybrid + rerank)", True, True),
            ("hybrid, no rerank", True, False),
            ("vector only + rerank", False, True),
            ("vector only, no rerank", False, False)]

if __name__ == "__main__":
    qs = yaml.safe_load(Path(sys.argv[1] if len(sys.argv) > 1 else "eval/questions.yaml").read_text())
    conn = connect()
    print(f"| Variant (chunk={config.CHUNK_TARGET_CHARS}) | hit@5 | correct | citations | not-found | traps |")
    print("| --- | --- | --- | --- | --- | --- |")
    for name, hybrid, rerank in VARIANTS:
        config.USE_HYBRID, config.USE_RERANK = hybrid, rerank
        m = metrics(evaluate(conn, qs, use_judge=True))
        print(f"| {name} | {fmt(m['hit@5'])} | {fmt(m['correct'])} | {fmt(m['citations'])} | "
              f"{fmt(m['not_found'])} | {fmt(m['trap_pass'])} |")
