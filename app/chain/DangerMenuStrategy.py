from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.chain.response_schema import DangerStrategyResponse
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
    4. 추상적이지 않고 구체적인 행동 가이드를 작성해주세요

    [작성 가이드 - 메뉴별 차별화 필수]
    - summary: 해당 메뉴의 핵심 문제를 메뉴명을 포함하여 구체적으로 작성
    - analysis_detail: 원가율, 공헌이익, 권장가격 중 가장 두드러진 문제점 1-2가지만 집중 분석
    - action_guide: 선택한 전략에 따라 구체적인 액션 제시
    
    {context}

    {format_instructions}
    """

DANGER_MENU_CONTEXT = """
    제공된 마진 등급 위험 메뉴 데이터를 기반으로 개선 가이드를 작성해주세요. 
    반드시 아래 두 가지 전략 중 하나를 선택하고, strategy_type 필드에 해당 코드를 반환해주세요:

    1. REMOVE_MENU: 해당 메뉴를 판매 대상에서 제외하거나 메뉴판 하단으로 이동
    2. ADJUST_PRICE: 권장가격 이상으로 가격을 조정

    각 메뉴의 원가율, 공헌이익, 권장가격을 고려하여 더 효과적인 전략을 선택해주세요.
    """

class DangerMenuChain:
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=1.0,
            max_output_tokens=6000,
            google_api_key=settings.GOOGLE_API_KEY 
        )
        self.parser = PydanticOutputParser(pydantic_object=DangerStrategyResponse)
        self.prompt = ChatPromptTemplate.from_messages([
                    ("system", get_system_prompt(DANGER_MENU_CONTEXT, self.parser)),
                    ("human", """
                    카페명:{cafe_name}
                    위험 메뉴 개수:{danger_menu_count}
                    {menu_details}
                    """)
                ])
        
        self.chain = self.prompt | self.llm | self.parser

danger_menu_chain = DangerMenuChain()