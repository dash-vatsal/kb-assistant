from kb.ratelimit import RateLimiter


def test_blocks_after_limit_and_recovers():
    rl = RateLimiter(max_calls=3, window_s=60)
    assert all(rl.allow("u", now=t) for t in (0, 1, 2))
    assert not rl.allow("u", now=3)
    assert rl.allow("other", now=3)          # per-user
    assert rl.allow("u", now=61)             # window slid
