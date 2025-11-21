from functools import wraps
from time import monotonic
from time import sleep
from threading import RLock


class RateLimiter:
    def __init__(self, rate_limit, replenish_seconds):
        self.capacity = rate_limit
        self._tokens = 0
        self.replenish_seconds = replenish_seconds
        self.refill_per_second = rate_limit / replenish_seconds
        self.last_update = monotonic()
        self._lock = RLock()

    def go_or_fail(self):
        with self._lock:
            if 1 <= self.tokens:
                self._tokens -= 1
                return True
            return False

    @property
    def expected_wait(self):
        with self._lock:
            tokens = self.tokens
            if tokens >= 1:
                return 0
            expected_wait = (1 - tokens) / self.refill_per_second
            return expected_wait

    def wait(self):
        while not self.go_or_fail():
            sleep(self.expected_wait)

    def __call__(self, wrapee):
        @wraps(wrapee)
        def wrapper(*args, **kw):
            self.wait()
            return wrapee(*args, **kw)
        return wrapper

    @property
    def tokens(self):
        with self._lock:
            now = monotonic()

            delta = self.refill_per_second * (now - self.last_update)
            self._tokens = min(self.capacity, self._tokens + delta)

            self.last_update = now

        return self._tokens

    def set_rate(self, rate_limit, replenish_seconds):
        self.capacity = rate_limit
        self._tokens = 0
        self.replenish_seconds = replenish_seconds
        self.refill_per_second = rate_limit / replenish_seconds
        self.last_update = monotonic()
