#!/usr/bin/env python3
"""web cache and tracker
"""
import requests
import redis
from functools import wraps
from typing import Optional
import time


class WebCacheTracker:
    def __init__(self, cache_expiry: int = 10):
        """Initialize Redis connection and set default cache expiry time
        
        Args:
            cache_expiry (int): Cache expiry time in seconds
        """
        self.store = redis.Redis()
        self.cache_expiry = cache_expiry

    def count_url_access(self, method):
        """Decorator counting URL accesses and caching responses
        
        Args:
            method: The function to wrap
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
                self.store.setex(cached_key, self.cache_expiry, html)
                
                # Increment access counter
                self.store.incr(count_key)
                
                return html

            except redis.RedisError as e:
                # Log error and continue without caching
                print(f"Redis error: {e}")
                return method(url)
            except Exception as e:
                raise RuntimeError(f"Error processing URL {url}: {str(e)}")

        return wrapper

    def get_url_count(self, url: str) -> Optional[int]:
        """Get number of times a URL has been accessed
        
        Args:
            url (str): The URL to check
            
        Returns:
            int: Number of accesses, or None if error
        """
        try:
            count = self.store.get(f"count:{url}")
            return int(count) if count else 0
        except redis.RedisError as e:
            print(f"Redis error getting count: {e}")
            return None

# Usage example
tracker = WebCacheTracker(cache_expiry=10)

@tracker.count_url_access
def get_page(url: str) -> str:
    """Returns HTML content of a URL
    
    Args:
        url (str): The URL to fetch
        
    Returns:
        str: The page HTML content
    """
    response = requests.get(url, timeout=5)
    response.raise_for_status()  # Raise exception for bad status codes
    return response.text
