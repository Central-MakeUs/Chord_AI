from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.chain.response_schema import CautionStrategyResponse
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate


def get_system_prompt(context: str, parser: PydanticOutputParser) -> str:
    format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")
    
    return f"""
    당신은 카페 운영자의 수익성 개선을 위한 전략 가이드 카드를 작성하는 전문가입니다

    [작성 규칙]
    1. JSON schema로 답하되 작성 포맷을 따라주세요
    2. 모든 답변은 '~해요', '~이에요/예요'와 같은 해요체(말 끝에 '요'를 붙이는 문체)를 사용해 주세요. 격식 있는 '하십시오체'나 딱딱한 말투는 피해 주세요. 특수기호는 사용하지 마세요
    3. 수치는 반드시 제공된 데이터 기준으로만 사용하되, 숫자는 모두 정수 형태(반올림)로 나타내주세요
    4. 아래 전략 유형 중 하나를 선택해서 작성해주세요. 

    [작성 가이드]
    summary, analysis_detail, action_guide는 무조건 선택한 전략 유형과 동일하게 작성해주세요.

    {context}

    {format_instructions}
    """

CAUTION_MENUS_CONTEXT = """
    제공된 마진 등급 주의 메뉴의 데이터를 기반으로 종합 개선 가이드를 작성해주세요.
    반드시 아래 두 가지 전략 중 하나를 선택하고, strategy_type 필드에 해당 코드를 반환해주세요:
    [전략 유형]
    1. ADJUST_PRICE: 권장 가격 이상으로 가격을 조정해 안전 단계로 메뉴 이동
    2. ADJUST_RECIPE: 레시피에서 체감 없는 재료 1가지를 조정해 안전 단계로 메뉴 이동 

    각 메뉴의 원가율, 공헌이익, 권장가격을 고려하여 더 효과적인 전략을 선택해주세요.
"""

class CautionMenusChain:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.8,
            max_tokens=2000,
            api_key=settings.OPENAI_API_KEY
        )   
        self.parser = PydanticOutputParser(pydantic_object=CautionStrategyResponse)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt(CAUTION_MENUS_CONTEXT, self.parser)),
            ("human", """
            카페명: {cafe_name}
            주의 메뉴 개수: {caution_menus_count}
            최저 공헌이익 메뉴 상세: {lowest_caution_menu_details}
            """)
        ])

        self.chain = self.prompt | self.llm | self.parser

caution_menus_chain = CautionMenusChain()