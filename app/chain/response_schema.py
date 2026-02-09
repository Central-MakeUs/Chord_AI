from pydantic import BaseModel, Field
from typing import List, Literal

class CautionStrategyResponse(BaseModel):
    summary: str = Field(description="행동 가이드 요약 (15자 이내 1문장)")
    analysis_detail: str = Field(description="분석(100자 이내 1~2문장)")
    action_guide: str = Field(description="행동 가이드(100자 이내 1~2문장)")
    strategy_type: Literal["ADJUST_PRICE", "ADJUST_RECIPE"] = Field(
        description="선택한 전략 코드 (ADJUST_PRICE: 가격 조정, ADJUST_RECIPE: 레시피 조정)"
    )

class HighMarginStrategyResponse(BaseModel):
    summary: str = Field(description="행동 가이드 요약 (15자 이내 1문장)")
    analysis_detail: str = Field(description="분석(100자 이내 1~2문장)")
    action_guide: str = Field(description="행동 가이드(100자 이내 1~2문장)")
    expected_effect: str = Field(description="기대 효과(50자 이내 1~2문장)")
    completion_phrase: str = Field(description="완료 후 표시 멘트(50자 이내 1~2문장)")

class StrategyResponse(BaseModel):
    summary: str = Field(description="행동 가이드 요약 (15자 이내 1문장)")
    analysis_detail: str = Field(description="분석(100자 이내 1~2문장)")
    action_guide: str = Field(description="행동 가이드(100자 이내 1~2문장)")
    strategy_type: Literal["REMOVE_MENU", "ADJUST_PRICE"] = Field(
            description="선택한 전략 코드 (REMOVE_MENU: 메뉴 제외/조정, ADJUST_PRICE: 가격 인상)"
        )


class DangerStrategyResponse(BaseModel):
    strategies: List[StrategyResponse] = Field(description="위험 메뉴별 전략 가이드 리스트")

DANGER_STRATEGY_TEMPLATES = {
    "REMOVE_MENU": {
        "expected_effect": "해당 메뉴를 제외하면, 카페 전체 평균 원가율이 {cost_rate_improvemnet}%p 개선될 수 있어요. 위험 메뉴를 정리하면, 동일한 매출 수준에서도 전체 수익 구조가 더 안정적이게 변해요."
    },
    "ADJUST_PRICE": {
        "expected_effect": "권장 가격인 {recommended_price}원으로 가격을 설정하면 이 메뉴 1잔당 남는 금액이 약 {contribution_improvement}원 증가해요."
    }
}

CAUTION_STRATEGY_TEMPLATES = {
    "ADJUST_PRICE": {
        "expected_effect": "권장 가격인 {recommended_price}원으로 가격을 설정하면 이 메뉴 1잔당 남는 금액이 약 {contribution_improvement}원 증가해요."
    },
    "ADJUST_RECIPE": {
        "expected_effect": "재료 조정으로 해당 메뉴가 안정 단계로 이동하면, 카페의 메뉴 구조 기준 평균 마진율이 약 {margin_rate_improvement}%p 개선돼요."
    }
}

