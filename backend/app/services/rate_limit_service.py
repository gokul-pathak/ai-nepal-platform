"""
Rate limiting service with in-memory sliding window implementation.

Provides a configurable, thread-safe rate limiting mechanism suitable for
MVP use. Can be replaced with Redis backend later without changing the interface.
"""

import logging
import time
from typing import Dict, List, Tuple
from threading import Lock
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitService:
    """
    In-memory rate limiter using sliding window algorithm.
    
    Tracks requests per key (e.g., session ID) over a time window.
    Thread-safe for concurrent access.
    """
    
    def __init__(
        self,
        requests_per_window: int = 20,
        window_seconds: int = 60,
        cleanup_interval_seconds: int = 300,
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_window: Max requests allowed within the time window
            window_seconds: Time window duration in seconds
            cleanup_interval_seconds: How often to clean expired entries (background task)
        """
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.cleanup_interval_seconds = cleanup_interval_seconds
        
        # Store: {key: [(timestamp, count), ...]}
        # Each key maps to a list of (timestamp, request_count) tuples
        self._store: Dict[str, List[Tuple[float, int]]] = {}
        self._lock = Lock()
        self._last_cleanup = time.time()
    
    def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed for the given key.
        
        Implements sliding window: counts requests within the last window_seconds.
        
        Args:
            key: Identifier for rate limiting (e.g., session ID)
        
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - self.window_seconds
            
            # Get existing timestamps for this key
            timestamps = self._store.get(key, [])
            
            # Filter out expired timestamps (outside the window)
            active_timestamps = [
                ts for ts in timestamps
                if ts[0] > window_start
            ]
            
            # Count total requests in the active window
            total_requests = sum(count for _, count in active_timestamps)
            
            if total_requests < self.requests_per_window:
                # Request allowed: add current timestamp
                active_timestamps.append((current_time, 1))
                self._store[key] = active_timestamps
                
                logger.info(
                    "rate_limit_check",
                    extra={
                        "key": key,
                        "requests_in_window": total_requests + 1,
                        "limit": self.requests_per_window,
                        "allowed": True,
                    },
                )
                return True
            else:
                # Rate limit exceeded
                logger.warning(
                    "rate_limit_exceeded",
                    extra={
                        "key": key,
                        "requests_in_window": total_requests,
                        "limit": self.requests_per_window,
                    },
                )
                return False
    
    def get_remaining_requests(self, key: str) -> int:
        """
        Get the number of remaining requests for a key before hitting the limit.
        
        Args:
            key: Identifier for rate limiting
        
        Returns:
            Number of requests remaining (0 if at limit)
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - self.window_seconds
            
            timestamps = self._store.get(key, [])
            active_timestamps = [
                ts for ts in timestamps
                if ts[0] > window_start
            ]
            
            total_requests = sum(count for _, count in active_timestamps)
            remaining = max(0, self.requests_per_window - total_requests)
            
            return remaining
    
    def get_reset_time(self, key: str) -> float:
        """
        Get Unix timestamp when the rate limit window resets for a key.
        
        Args:
            key: Identifier for rate limiting
        
        Returns:
            Unix timestamp of when the oldest request in the window expires
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - self.window_seconds
            
            timestamps = self._store.get(key, [])
            active_timestamps = [
                ts for ts in timestamps
                if ts[0] > window_start
            ]
            
            if not active_timestamps:
                # No active requests, reset time is now
                return current_time
            
            # Reset time is when the oldest request expires
            oldest_request_time = min(ts[0] for ts in active_timestamps)
            reset_time = oldest_request_time + self.window_seconds
            
            return reset_time
    
    def cleanup_expired(self) -> None:
        """
        Remove expired entries from the store.
        
        Cleans up keys with no active requests in the current window.
        Automatically called periodically or can be invoked manually.
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - self.window_seconds
            
            keys_to_remove = []
            
            for key, timestamps in self._store.items():
                active_timestamps = [
                    ts for ts in timestamps
                    if ts[0] > window_start
                ]
                
                if not active_timestamps:
                    keys_to_remove.append(key)
                else:
                    self._store[key] = active_timestamps
            
            for key in keys_to_remove:
                del self._store[key]
            
            if keys_to_remove:
                logger.info(
                    "rate_limit_cleanup",
                    extra={"cleaned_keys_count": len(keys_to_remove)},
                )
            
            self._last_cleanup = current_time
    
    def should_cleanup(self) -> bool:
        """Check if cleanup is due based on cleanup interval."""
        return (time.time() - self._last_cleanup) > self.cleanup_interval_seconds


# Global instance
_rate_limit_service: RateLimitService | None = None


def get_rate_limit_service(
    requests_per_window: int = 20,
    window_seconds: int = 60,
) -> RateLimitService:
    """
    Get or create the global rate limit service instance.
    
    Args:
        requests_per_window: Max requests allowed within the time window
        window_seconds: Time window duration in seconds
    
    Returns:
        RateLimitService instance
    """
    global _rate_limit_service
    if _rate_limit_service is None:
        _rate_limit_service = RateLimitService(
            requests_per_window=requests_per_window,
            window_seconds=window_seconds,
        )
    return _rate_limit_service


def reset_rate_limit_service() -> None:
    """Reset the global rate limit service (useful for testing)."""
    global _rate_limit_service
    _rate_limit_service = None
