import os
import sys

os.environ["JWT_SECRET"] = "test-secret"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.main import _resolve_target
from app.rate_limit import SlidingWindowRateLimiter


def test_route_resolution_maps_to_correct_service():
    base, path = _resolve_target("/events")
    assert base == settings.event_service_url

    base, path = _resolve_target("/events/abc123/publish")
    assert base == settings.event_service_url

    base, path = _resolve_target("/bookings/reserve")
    assert base == settings.booking_service_url

    base, path = _resolve_target("/auth/login")
    assert base == settings.identity_service_url

    assert _resolve_target("/unknown-service") is None


def test_rate_limiter_blocks_after_threshold():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
    results = [limiter.allow("client-a") for _ in range(5)]
    assert results == [True, True, True, False, False]

    # a different client has its own independent budget
    assert limiter.allow("client-b") is True
