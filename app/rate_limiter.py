"""
Simple Rate Limiter
Prevents spamming of expensive LLM endpoints.
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException
from functools import wraps

# In-memory store: {ip_address: [timestamps]}
# Note: For massive scale, use Redis. For this app, memory/file is fine.
_request_history = defaultdict(list)

def rate_limit(requests: int, window_seconds: int):
    """
    Decorator to rate limit a route.
    Args:
        requests: Max number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Try to get real client IP (handling proxies like Railway/Render)
            ip = request.headers.get("x-forwarded-for") or request.client.host
            now = time.time()
            
            # Clean up old timestamps
            _request_history[ip] = [t for t in _request_history[ip] if now - t < window_seconds]
            
            if len(_request_history[ip]) >= requests:
                # Calculate wait time
                wait = int(window_seconds - (now - _request_history[ip][0]))
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Too many requests",
                        "message": f"Please slow down. You can try again in {wait} seconds.",
                        "wait_seconds": wait
                    }
                )
            
            _request_history[ip].append(now)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
