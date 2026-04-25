import ipaddress
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("mlx-serve")


class IPAllowListMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_cidrs: list[str]):
        super().__init__(app)
        self.allowed_networks = [ipaddress.ip_network(c) for c in allowed_cidrs]

    async def dispatch(self, request: Request, call_next):
        client_ip = ipaddress.ip_address(request.client.host)
        if not any(client_ip in net for net in self.allowed_networks):
            return JSONResponse(
                status_code=403,
                content={"detail": f"Forbidden: {request.client.host}"},
            )
        return await call_next(request)


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            '%s "%s %s" %d %.3fs',
            request.client.host,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response
