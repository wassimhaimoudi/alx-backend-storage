#!/usr/bin/env python3
"""Web caching and access tracking implementation using Redis."""

import requests
import redis
from functools import wraps
from typing import Optional


class WebCacheTracker:
    """Handle web page caching and access tracking using Redis."""

    def __init__(self, cache_expiry: int = 10):
        """Initialize Redis connection and cache settings.

        Args:
            cache_expiry: Number of seconds before cached items expire.
        """
        self.store = redis.Redis()
        self.cache_expiry = cache_expiry

    def count_url_access(self, method):
        """Count URL accesses and cache responses.

        Args:
            method: The function to wrap.

        Returns:
            A wrapped function that implements caching and access counting.

        Raises:
            ValueError: If the URL is empty.
            RuntimeError: If URL processing fails.
        """
        @wraps(method)
        def wrapper(url: str) -> str:
            if not url:
                raise ValueError("URL cannot be empty")

            cached_key = f"cached:{url}"
            count_key = f"count:{url}"

            try:
                # Check cache first
                cached_data = self.store.get(cached_key)
                if cached_data:
                    # Still increment counter for cached hits
                    self.store.incr(count_key)
                    return cached_data.decode("utf-8")

                # Get fresh data
                html = method(url)

                # Store in cache with expiry
                self.store.setex(
                    name=cached_key,
                    time=self.cache_expiry,
                    value=html
                )

                # Increment access counter
                self.store.incr(count_key)

                return html

            except redis.RedisError as e:
                # Log error and continue without caching
                print(f"Redis error: {e}")
                return method(url)
            except Exception as e:
                raise RuntimeError(
                    f"Error processing URL {url}: {str(e)}"
                )

        return wrapper

    def get_url_count(self, url: str) -> Optional[int]:
        """Get number of times a URL has been accessed.

        Args:
            url: The URL to check.

        Returns:
            Number of accesses, or None if an error occurs.
        """
        try:
            count = self.store.get(f"count:{url}")
            return int(count) if count else 0
        except redis.RedisError as e:
            print(f"Redis error getting count: {e}")
            return None


def create_tracker(cache_expiry: int = 10) -> WebCacheTracker:
    """Create a new WebCacheTracker instance.

    Args:
        cache_expiry: Number of seconds before cached items expire.

    Returns:
        A configured WebCacheTracker instance.
    """
    return WebCacheTracker(cache_expiry=cache_expiry)


# Example usage
tracker = create_tracker(cache_expiry=10)


@tracker.count_url_access
def get_page(url: str) -> str:
    """Retrieve HTML content from a URL.

    Args:
        url: The URL to fetch.

    Returns:
        The page HTML content.

    Raises:
        requests.RequestException: If the HTTP request fails.
    """
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.text
