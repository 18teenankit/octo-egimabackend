from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        
    async def dispatch(self, request: Request, call_next):
        # Allow CORS preflight without rate limiting
        if request.method == "OPTIONS":
            return await call_next(request)
        # Get client IP
        client_ip = request.client.host
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc"]:
            return await call_next(request)
            
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        minute_ago = current_time - 60
        while self.requests[client_ip] and self.requests[client_ip][0] < minute_ago:
            self.requests[client_ip].popleft()
            
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed"
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + 60))
                }
            )
            
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response