import time
from collections import defaultdict, deque
from threading import Lock


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            window = self._hits[key]
            while window and window[0] < now - self.window_seconds:
                window.popleft()
            if len(window) >= self.max_requests:
                return False
            window.append(now)
            return True
