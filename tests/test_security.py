"""Integration tests: need Postgres + Bedrock + `make seed`. These are the 'never cut' tests (Days 25-26)."""
from pathlib import Path
import pytest
import yaml
from kb.answer import answer_question
from kb.db import connect

pytestmark = pytest.mark.integration
SPEC = yaml.safe_load((Path(__file__).parent.parent / "eval" / "security_traps.yaml").read_text())


@pytest.fixture(scope="module")
def conn():
    c = connect()
    yield c
    c.close()


def _blob(res):
    chunks = " ".join(h["text"] for h in res["_hits"])
    return res["answer"] + " " + chunks


@pytest.mark.parametrize("t", SPEC["traps"] + SPEC["injection"], ids=lambda t: f'{t["user"]}:{t["question"][:40]}')
def test_forbidden_never_leaks(conn, t):
    res = answer_question(conn, t["question"], t["user"])
    blob = _blob(res)
    for bad in t["forbidden"]:
        assert bad not in blob, f"LEAK: {bad}"


@pytest.mark.parametrize("t", SPEC["positive_controls"], ids=lambda t: t["user"])
def test_allowed_user_can_see(conn, t):
    res = answer_question(conn, t["question"], t["user"])
    assert res["found"]
    assert any(s.lower() in res["answer"].lower() for s in t["must_contain_any"])


def test_unknown_user_sees_nothing(conn):
    res = answer_question(conn, "What is the code review process?", "does_not_exist")
    assert not res["found"] and not res["_hits"]
