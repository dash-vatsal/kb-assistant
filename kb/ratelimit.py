"""In-memory sliding-window rate limiter (per user). Fine for one API process; use Redis/API gateway for several."""
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_calls: int = 20, window_s: int = 60):
        self.max_calls, self.window_s = max_calls, window_s
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        q = self._hits[key]
        while q and now - q[0] >= self.window_s:
            q.popleft()
        if len(q) >= self.max_calls:
            return False
        q.append(now)
        return True
