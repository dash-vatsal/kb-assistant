"""T-054: score Amazon Bedrock Knowledge Bases retrieval on the SAME questions (hit@5 only).
   KB_ID=XXXXXXXXXX python scripts/bedrock_kb_benchmark.py eval/questions.yaml
Setup (console): create a Knowledge Base on the same Confluence space (or an S3 export of it), sync it.
Hit = an expected_url appears in the location of any of the top 5 results.
Also record by hand (docs/bedrock_kb_comparison.md): per-user permission filtering support (metadata filters),
not-found control, sync/deletion behaviour, cost, setup time. Use only non-client content for the benchmark."""
import json
import os
import sys
from pathlib import Path
import boto3
import yaml

if __name__ == "__main__":
    kb_id = os.environ["KB_ID"]
    client = boto3.client("bedrock-agent-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    qs = [q for q in yaml.safe_load(Path(sys.argv[1] if len(sys.argv) > 1 else "eval/questions.yaml").read_text())
          if q["type"] == "answer"]
    hits = 0
    for q in qs:
        r = client.retrieve(knowledgeBaseId=kb_id, retrievalQuery={"text": q["question"]},
                            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}})
        blob = " ".join(json.dumps(x.get("location", {})) for x in r["retrievalResults"])
        ok = any(u in blob for u in q.get("expected_urls", []))
        hits += ok
        print(("HIT  " if ok else "MISS ") + q["id"] + "  " + q["question"][:70])
    print(f"Bedrock KB hit@5: {hits}/{len(qs)} = {hits / len(qs):.0%}" if qs else "no answerable questions")
