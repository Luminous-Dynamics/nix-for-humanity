"""Rate limiting and DDoS protection for Nix for Humanity."""

import hashlib
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Deque, Dict, Optional, Tuple, TypeVar

import redis
from flask import Flask, Request, jsonify, request

T = TypeVar("T")


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    
    requests: int = 100  # Number of requests allowed
    window: int = 60  # Time window in seconds
    burst: int = 10  # Burst allowance
    block_duration: int = 300  # Block duration in seconds for violations


class InMemoryRateLimiter:
    """In-memory rate limiter using sliding window."""
    
    def __init__(self, config: RateLimitConfig):
        """Initialize in-memory rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.blocked: Dict[str, float] = {}
    
    def _get_key(self, identifier: str) -> str:
        """Get rate limit key for identifier.
        
        Args:
            identifier: User/IP identifier
            
        Returns:
            Rate limit key
        """
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def _clean_old_requests(self, key: str, current_time: float) -> None:
        """Remove requests outside the time window.
        
        Args:
            key: Rate limit key
            current_time: Current timestamp
        """
        window_start = current_time - self.config.window
        
        # Remove old requests
        while self.requests[key] and self.requests[key][0] < window_start:
            self.requests[key].popleft()
    
    def _is_blocked(self, key: str, current_time: float) -> bool:
        """Check if identifier is blocked.
        
        Args:
            key: Rate limit key
            current_time: Current timestamp
            
        Returns:
            True if blocked, False otherwise
        """
        if key in self.blocked:
            if current_time < self.blocked[key]:
                return True
            else:
                # Unblock if duration expired
                del self.blocked[key]
        return False
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """Check if request is within rate limit.
        
        Args:
            identifier: User/IP identifier
            
        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        key = self._get_key(identifier)
        current_time = time.time()
        
        # Check if blocked
        if self._is_blocked(key, current_time):
            retry_after = int(self.blocked[key] - current_time)
            return False, retry_after
        
        # Clean old requests
        self._clean_old_requests(key, current_time)
        
        # Check rate limit
        request_count = len(self.requests[key])
        
        if request_count >= self.config.requests:
            # Block for violations
            self.blocked[key] = current_time + self.config.block_duration
            return False, self.config.block_duration
        
        # Check burst limit
        if request_count > 0:
            recent_requests = [
                t for t in self.requests[key]
                if t > current_time - 1  # Last second
            ]
            if len(recent_requests) >= self.config.burst:
                return False, 1
        
        # Allow request
        self.requests[key].append(current_time)
        return True, None
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier.
        
        Args:
            identifier: User/IP identifier
        """
        key = self._get_key(identifier)
        if key in self.requests:
            del self.requests[key]
        if key in self.blocked:
            del self.blocked[key]


class RedisRateLimiter:
    """Redis-based distributed rate limiter."""
    
    def __init__(self, redis_client: redis.Redis, config: RateLimitConfig):
        """Initialize Redis rate limiter.
        
        Args:
            redis_client: Redis client instance
            config: Rate limit configuration
        """
        self.redis = redis_client
        self.config = config
    
    def _get_key(self, identifier: str) -> str:
        """Get rate limit key for identifier.
        
        Args:
            identifier: User/IP identifier
            
        Returns:
            Rate limit key
        """
        return f"rate_limit:{hashlib.md5(identifier.encode()).hexdigest()}"
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """Check if request is within rate limit using Redis.
        
        Args:
            identifier: User/IP identifier
            
        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        key = self._get_key(identifier)
        blocked_key = f"{key}:blocked"
        
        try:
            # Check if blocked
            if self.redis.exists(blocked_key):
                ttl = self.redis.ttl(blocked_key)
                return False, max(ttl, 1)
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            current_time = time.time()
            window_start = current_time - self.config.window
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Execute pipeline
            _, request_count = pipe.execute()
            
            # Check rate limit
            if request_count >= self.config.requests:
                # Block for violations
                self.redis.setex(blocked_key, self.config.block_duration, 1)
                return False, self.config.block_duration
            
            # Check burst limit (requests in last second)
            burst_start = current_time - 1
            burst_count = self.redis.zcount(key, burst_start, current_time)
            
            if burst_count >= self.config.burst:
                return False, 1
            
            # Add current request
            pipe = self.redis.pipeline()
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, self.config.window)
            pipe.execute()
            
            return True, None
            
        except redis.RedisError:
            # If Redis fails, allow request (fail open)
            return True, None
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier.
        
        Args:
            identifier: User/IP identifier
        """
        key = self._get_key(identifier)
        blocked_key = f"{key}:blocked"
        
        try:
            self.redis.delete(key, blocked_key)
        except redis.RedisError:
            pass


class RateLimiter:
    """Rate limiter with Redis fallback to in-memory."""
    
    def __init__(
        self,
        config: RateLimitConfig,
        redis_client: Optional[redis.Redis] = None,
    ):
        """Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.config = config
        
        # Use Redis if available, otherwise in-memory
        if redis_client:
            try:
                redis_client.ping()
                self.backend = RedisRateLimiter(redis_client, config)
                self.distributed = True
            except redis.RedisError:
                self.backend = InMemoryRateLimiter(config)
                self.distributed = False
        else:
            self.backend = InMemoryRateLimiter(config)
            self.distributed = False
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """Check if request is within rate limit.
        
        Args:
            identifier: User/IP identifier
            
        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        return self.backend.check_rate_limit(identifier)
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier.
        
        Args:
            identifier: User/IP identifier
        """
        self.backend.reset(identifier)


def rate_limit(
    requests: int = 100,
    window: int = 60,
    burst: int = 10,
    identifier: Optional[Callable[[Request], str]] = None,
) -> Callable:
    """Decorator for rate limiting Flask routes.
    
    Args:
        requests: Number of requests allowed
        window: Time window in seconds
        burst: Burst allowance
        identifier: Function to extract identifier from request
        
    Returns:
        Decorated function
    """
    config = RateLimitConfig(
        requests=requests,
        window=window,
        burst=burst,
    )
    
    def get_identifier(req: Request) -> str:
        """Get identifier from request.
        
        Args:
            req: Flask request
            
        Returns:
            Identifier string
        """
        if identifier:
            return identifier(req)
        
        # Default: Use IP address
        return req.remote_addr or "unknown"
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Get rate limiter from app context
            from flask import current_app
            
            limiter = getattr(current_app, "rate_limiter", None)
            if not limiter:
                # No rate limiter configured, allow request
                return func(*args, **kwargs)
            
            # Check rate limit
            req_identifier = get_identifier(request)
            allowed, retry_after = limiter.check_rate_limit(req_identifier)
            
            if not allowed:
                # Rate limit exceeded
                response = jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                })
                response.status_code = 429
                response.headers["Retry-After"] = str(retry_after)
                response.headers["X-RateLimit-Limit"] = str(config.requests)
                response.headers["X-RateLimit-Window"] = str(config.window)
                return response
            
            # Add rate limit headers
            response = func(*args, **kwargs)
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(config.requests)
                response.headers["X-RateLimit-Window"] = str(config.window)
            
            return response
        
        return wrapper
    return decorator


def setup_rate_limiting(
    app: Flask,
    config: Optional[RateLimitConfig] = None,
    redis_client: Optional[redis.Redis] = None,
) -> RateLimiter:
    """Set up rate limiting for Flask app.
    
    Args:
        app: Flask application
        config: Rate limit configuration
        redis_client: Optional Redis client
        
    Returns:
        Configured rate limiter
    """
    if config is None:
        config = RateLimitConfig()
    
    # Create rate limiter
    limiter = RateLimiter(config, redis_client)
    
    # Attach to app
    app.rate_limiter = limiter
    
    # Add before_request handler for global rate limiting
    @app.before_request
    def check_global_rate_limit():
        """Check global rate limit before each request."""
        if not hasattr(app, "rate_limiter"):
            return
        
        # Skip rate limiting for static files
        if request.endpoint and request.endpoint.startswith("static"):
            return
        
        # Get identifier
        identifier = request.remote_addr or "unknown"
        
        # Check rate limit
        allowed, retry_after = app.rate_limiter.check_rate_limit(identifier)
        
        if not allowed:
            response = jsonify({
                "error": "Rate limit exceeded",
                "retry_after": retry_after,
            })
            response.status_code = 429
            response.headers["Retry-After"] = str(retry_after)
            return response
    
    return limiter