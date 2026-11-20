import json
import time
import boto3
from botocore.exceptions import ClientError
from kb import config

_client = None


def client():
    global _client
    if _client is None:
        _client = boto3.client("bedrock-runtime", region_name=config.AWS_REGION)
    return _client


def _retry(fn, tries=5):
    for i in range(tries):
        try:
            return fn()
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ("ThrottlingException", "ModelTimeoutException") and i < tries - 1:
                time.sleep(2 ** i)
                continue
            raise


def embed(text: str) -> list[float]:
    body = json.dumps({"inputText": text[:20000], "dimensions": config.EMBED_DIM, "normalize": True})
    r = _retry(lambda: client().invoke_model(
        modelId=config.EMBED_MODEL_ID, body=body,
        contentType="application/json", accept="application/json"))
    return json.loads(r["body"].read())["embedding"]


def generate(system: str, user: str, model_id: str | None = None,
             max_tokens: int = 1024, temperature: float = 0.0) -> str:
    r = _retry(lambda: client().converse(
        modelId=model_id or config.ANSWER_MODEL_ID,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature}))
    return r["output"]["message"]["content"][0]["text"]
