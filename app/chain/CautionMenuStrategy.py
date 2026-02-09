from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.chain.response_schema import StrategyResponse
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate


def get_system_prompt(context: str, parser: PydanticOutputParser) -> str:
    format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")
    
    return f"""
    당신은 카페 운영자의 수익성 개선을 위한 전략 가이드 카드를 작성하는 전문가입니다

    [작성 규칙]
    1. JSON schema로 답하되 작성 포맷을 따라주세요
    2. 톤은 전반적으로 '~요'체로 작성하되, 특수기호는 사용하지 마세요
    3. 수치는 반드시 제공된 데이터 기준으로만 사용하되, 숫자는 모두 정수 형태(반올림)로 나타내주세요
    4. 추상적이지 않고 구체적인 행동 가이드를 작성해주세요

    [작성 가이드 - 메뉴별 차별화 필수]
    
    {context}

    {format_instructions}
    """

CAUTION_MENUS_CONTEXT = """
제공된 마진 등급 주의 메뉴들의 데이터를 기반으로 종합 개선 가이드를 작성해주세요.

[전략 선택 기준]
공헌이익이 가장 낮은 메뉴 1개를 타겟으로 선정하고, 아래 두 가지 전략 중 하나를 선택해주세요:

1. ADJUST_PRICE: 가격 조정 전략
   - 선택 조건: 권장가격과 현재 판매가 차이가 500원 이상일 때
   - 권장가격 대비 현재가가 낮아 가격 인상 여력이 있을 때
   
2. ADJUST_RECIPE: 레시피 조정 전략  
   - 선택 조건: 가격 조정 여력이 부족하거나(300원 미만 차이)
   - 원가율이 높아 재료비 절감이 더 효과적일 때

target_menu_name 필드에는 반드시 주의 메뉴 중 공헌이익이 가장 낮은 메뉴명을 정확히 입력해주세요.
"""

class CautionMenusChain:

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=1.0,
            max_output_tokens=2000,
            google_api_key=settings.GOOGLE_API_KEY,
        )        
        self.parser = PydanticOutputParser(pydantic_object=StrategyResponse)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt(CAUTION_MENUS_CONTEXT, self.parser)),
            ("human", """
            카페명:{cafe_name}
            주의 메뉴 개수:{caution_menu_count}
            주의 메뉴 목록(메뉴명/원가율/공헌이익):{caution_menu_details}
            최저 공헌이익 메뉴:{lowest_contribution_menu_name} (공헌이익: {lowest_contribuition_menu_margin}%)
            """)
        ])

        self.chain = self.prompt | self.llm | self.parser

caution_menus_chain = CautionMenusChain()