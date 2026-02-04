from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.base_response import ErrorResponse, ApiResponse, ErrorCode
import traceback
import logging
import json

logger = logging.getLogger(__name__)

class ResponseMiddleware(BaseHTTPMiddleware):
    """응답 통일"""
    async def dispatch(self, request, call_next):
        if request.url.path in ["/openapi.json", "/docs", "/redoc"]:
            return await call_next(request)
        
        try:
            response = await call_next(request)

            if response.status_code >= 400:
                return response

            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return response
            
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            try:
                raw = json.loads(body.decode()) if body else None
            except Exception:
                return JSONResponse(status_code=response.status_code, content=body)

            if isinstance(raw, dict) and "success" in raw:
                return JSONResponse(status_code=response.status_code, content=raw)

            wrapped = ApiResponse.of(data=raw).model_dump(exclude_none=True)
            return JSONResponse(status_code=response.status_code, content=wrapped)
        except Exception as exc:
            logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse.of(ErrorCode.INTERNAL_SERVER_ERROR).model_dump(exclude_none=True)
            )
            