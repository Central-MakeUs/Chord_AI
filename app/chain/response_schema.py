from pydantic import BaseModel, Field
from typing import List 

class StrategyResponse(BaseModel):
    summary: str = Field(description="행동 가이드 요약 (15자 이내 1문장)")
    analysis_detail: str = Field(description="분석(100자 이내 1~2문장)")
    action_guide: str = Field(description="행동 가이드(100자 이내 1~2문장)")
    strategy_type: str = Field(description="선택한 전략 코드")

class HighMarginStrategyResponse(BaseModel):
    summary: str = Field(description="행동 가이드 요약 (15자 이내 1문장)")
    analysis_detail: str = Field(description="분석(100자 이내 1~2문장)")
    action_guide: str = Field(description="행동 가이드(100자 이내 1~2문장)")
    expected_effect: str = Field(description="기대 효과(50자 이내 1~2문장)")
    completion_phrase: str = Field(description="완료 후 표시 멘트(50자 이내 1~2문장)")

class DangerStrategyResponse(BaseModel):
    strategies: List[StrategyResponse] = Field(description="위험 메뉴별 전략 가이드 리스트")
