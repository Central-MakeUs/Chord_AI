from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.base_response import BusinessException, ErrorCode, ErrorResponse

def create_exception_handlers(app):
    """예외 핸들러"""
    
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        """비즈니스 예외 처리"""
        return JSONResponse(
            status_code=exc.error_code.get_status_code(),
            content=ErrorResponse.of(error=exc.error_code, errors=None).model_dump(exclude_none=True)
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Validation 에러 처리"""
        errors = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            errors[field] = error["msg"]
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse.of(
                error= ErrorCode.INVALID_INPUT_VALUE,
                errors=errors
            ).model_dump(exclude_none=True))
        
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP 예외 처리"""
        error_code_map = {
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            405: ErrorCode.METHOD_NOT_ALLOWED,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }
        
        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.of(error=error_code, errors=None).model_dump(exclude_none=True)
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
        """Starlette HTTP 예외 처리"""
        error_code_map = {
            404: ErrorCode.NOT_FOUND,
            405: ErrorCode.METHOD_NOT_ALLOWED,
        }
        
        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.of(error=error_code, errors=None).model_dump(exclude_none=True)
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """일반 예외 처리"""
        import traceback
        import logging
        
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse.of(error=ErrorCode.INTERNAL_SERVER_ERROR, errors=None).model_dump(exclude_none=True)
        )
