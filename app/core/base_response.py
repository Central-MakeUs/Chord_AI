from pydantic import BaseModel, BaseModel, Field
from typing import Generic, TypeVar, Optional, Dict
from datetime import datetime
from fastapi import status, HTTPException
from enum import Enum

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """성공 응답"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def of(cls, data: Optional[T] = None):
        return cls(data=data)

# Error Code (ENUM)
class ErrorCode(str, Enum):
    # 공통 에러
    INVALID_INPUT_VALUE = "COMMON_001"
    METHOD_NOT_ALLOWED = "COMMON_002"
    INTERNAL_SERVER_ERROR = "COMMON_003"
    INVALID_TYPE_VALUE = "COMMON_004"
    MISSING_REQUEST_PARAMETER = "COMMON_005"
    SERVICE_UNAVAILABLE = "COMMON_006"
    NOT_FOUND = "COMMON_007"
    
    # 인증/인가
    UNAUTHORIZED = "AUTH_001"
    FORBIDDEN = "AUTH_002"
    INVALID_TOKEN = "AUTH_003"
    
    def get_message(self) -> str:
        messages = {
            "COMMON_001": "입력값이 올바르지 않습니다",
            "COMMON_002": "지원하지 않는 HTTP 메서드입니다",
            "COMMON_003": "서버 내부 오류가 발생했습니다",
            "COMMON_004": "잘못된 타입입니다",
            "COMMON_005": "필수 파라미터가 누락되었습니다",
            "COMMON_006": "서비스에 연결할 수 없습니다",
            "COMMON_007": "요청하신 자원을 찾을 수 없습니다",
            "AUTH_001": "인증이 필요합니다",
            "AUTH_002": "접근 권한이 없습니다",
            "AUTH_003": "유효하지 않은 토큰입니다",
        }
        return messages.get(self.value, "알 수 없는 오류")
    
    def get_status_code(self) -> int:
        status_codes = {
            "COMMON_001": status.HTTP_400_BAD_REQUEST,
            "COMMON_002": status.HTTP_405_METHOD_NOT_ALLOWED,
            "COMMON_003": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "COMMON_004": status.HTTP_400_BAD_REQUEST,
            "COMMON_005": status.HTTP_400_BAD_REQUEST,
            "COMMON_006": status.HTTP_503_SERVICE_UNAVAILABLE,
            "COMMON_007": status.HTTP_404_NOT_FOUND,
            "AUTH_001": status.HTTP_401_UNAUTHORIZED,
            "AUTH_002": status.HTTP_403_FORBIDDEN,
            "AUTH_003": status.HTTP_401_UNAUTHORIZED,
        }
        return status_codes.get(self.value, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    code: str
    message: str
    errors: Optional[Dict[str, str]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    """datetime 직렬화"""
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def of(cls, error: ErrorCode, errors: Optional[Dict[str, str]]=None):
        return cls(code=error.value, message=error.get_message(), errors=errors)



# 비즈니스 예외
class BusinessException(Exception):
    def __init__(self, error_code: ErrorCode):
        self.error_code = error_code