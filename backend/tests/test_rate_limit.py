"""Tests for rate limiting service."""

import pytest
import time
from unittest.mock import patch

from app.services.rate_limit_service import (
    RateLimitService,
    get_rate_limit_service,
    reset_rate_limit_service,
)


class TestRateLimitService:
    """Test suite for RateLimitService."""

    def test_allows_requests_within_limit(self):
        """Test that requests are allowed within the rate limit."""
        limiter = RateLimitService(requests_per_window=3, window_seconds=60)
        
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is True

    def test_rejects_requests_exceeding_limit(self):
        """Test that requests are rejected when limit is exceeded."""
        limiter = RateLimitService(requests_per_window=2, window_seconds=60)
        
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is False  # Third request rejected

    def test_separate_sessions_have_separate_limits(self):
        """Test that different sessions have separate rate limits."""
        limiter = RateLimitService(requests_per_window=2, window_seconds=60)
        
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is False
        
        # Different session should have its own limit
        assert limiter.is_allowed("session2") is True
        assert limiter.is_allowed("session2") is True
        assert limiter.is_allowed("session2") is False

    def test_get_remaining_requests(self):
        """Test remaining requests calculation."""
        limiter = RateLimitService(requests_per_window=5, window_seconds=60)
        
        assert limiter.get_remaining_requests("session1") == 5
        limiter.is_allowed("session1")
        assert limiter.get_remaining_requests("session1") == 4
        limiter.is_allowed("session1")
        assert limiter.get_remaining_requests("session1") == 3

    def test_get_remaining_requests_zero_when_limit_exceeded(self):
        """Test that remaining requests is 0 when limit is exceeded."""
        limiter = RateLimitService(requests_per_window=2, window_seconds=60)
        
        limiter.is_allowed("session1")
        limiter.is_allowed("session1")
        
        assert limiter.get_remaining_requests("session1") == 0

    def test_window_expiration(self):
        """Test that requests are allowed again after window expires."""
        limiter = RateLimitService(requests_per_window=2, window_seconds=1)
        
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is True
        assert limiter.is_allowed("session1") is False  # Limit exceeded
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed("session1") is True

    def test_get_reset_time(self):
        """Test that reset time is calculated correctly."""
        limiter = RateLimitService(requests_per_window=5, window_seconds=60)
        
        current_time = time.time()
        limiter.is_allowed("session1")
        reset_time = limiter.get_reset_time("session1")
        
        # Reset time should be approximately current_time + 60 seconds (within 2 second tolerance for timing)
        assert reset_time > current_time
        assert reset_time <= current_time + 62  # Allow 2 second tolerance for timing variance

    def test_get_reset_time_empty_session(self):
        """Test that reset time for empty session is current time."""
        limiter = RateLimitService(requests_per_window=5, window_seconds=60)
        
        current_time = time.time()
        reset_time = limiter.get_reset_time("session1")
        
        # Reset time should be approximately current time
        assert reset_time >= current_time - 1  # Allow 1 second tolerance
        assert reset_time <= current_time + 1

    def test_cleanup_expired_entries(self):
        """Test that cleanup removes expired entries."""
        limiter = RateLimitService(
            requests_per_window=3,
            window_seconds=1,
            cleanup_interval_seconds=1,
        )
        
        # Create multiple sessions
        limiter.is_allowed("session1")
        limiter.is_allowed("session2")
        
        # Store should have entries
        assert len(limiter._store) == 2
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Cleanup should remove expired entries
        limiter.cleanup_expired()
        assert len(limiter._store) == 0

    def test_cleanup_interval_check(self):
        """Test that cleanup interval is respected."""
        limiter = RateLimitService(
            requests_per_window=3,
            window_seconds=60,
            cleanup_interval_seconds=1,  # 1 second interval for testing
        )
        
        # Immediately after creation, cleanup is not due (just initialized)
        assert limiter.should_cleanup() is False
        
        # Wait for interval to pass
        time.sleep(1.1)
        
        # Should be due for cleanup after interval expires
        assert limiter.should_cleanup() is True
        
        # After cleanup, should not be due again
        limiter.cleanup_expired()
        assert limiter.should_cleanup() is False

    def test_global_service_instance(self):
        """Test that get_rate_limit_service returns singleton instance."""
        reset_rate_limit_service()
        
        service1 = get_rate_limit_service(requests_per_window=5, window_seconds=60)
        service1.is_allowed("session1")
        
        # Get service again - should be same instance
        service2 = get_rate_limit_service()
        
        assert service1 is service2
        assert service2.get_remaining_requests("session1") == 4

    def test_thread_safety(self):
        """Test basic thread safety (concurrent access doesn't corrupt state)."""
        import threading
        
        limiter = RateLimitService(requests_per_window=1000, window_seconds=60)
        results = []
        
        def make_requests():
            for _ in range(10):
                results.append(limiter.is_allowed("session1"))
        
        threads = [threading.Thread(target=make_requests) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All requests should be allowed (1000 limit vs 50 requests)
        assert all(results)
        assert limiter.get_remaining_requests("session1") == 950

