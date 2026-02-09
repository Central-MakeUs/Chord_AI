from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.chain.response_schema import StrategyResponse, DangerStrategyResponse, HighMarginStrategyResponse
from langchain_core.output_parsers import PydanticOutputParser
from app.schemas.prompt_data import DangerMenu, CautionMenus, HighMarginMenus
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

    [작성 가이드]
    {context}

    [길이 가이드]
    summary: 15자 이내 1문장
    analysis_detail: 100자 이내 1~2문장 
    action_guide: 100자 이내 1~2문장

    {format_instructions}
    """
def get_high_margin_strategy_system_prompt(context: str, parser: PydanticOutputParser) -> str:
    format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")
    
    return f"""
    당신은 카페 운영자의 수익성 개선을 위한 전략 가이드 카드를 작성하는 전문가입니다

    [작성 규칙]
    1. JSON schema로 답하되 작성 포맷을 따라주세요
    2. 톤은 '~요'체로 작성하되, 특수기호는 사용하지 마세요
    3. 수치는 반드시 제공된 데이터 기준으로만 사용하되, 숫자는 모두 정수 형태(반올림)로 나타내주세요
    4. 추상적이지 않고 구체적인 행동 가이드를 작성해주세요

    [작성 가이드]
    {context}

    [길이 가이드]
    summary: 15자 이내 1문장
    analysis_detail: 100자 이내 1~2문장 
    action_guide: 100자 이내 1~2문장
    expected_effect: 50자 이내 1~2문장
    completion_phrase: 50자 이내 1~2문장

    {format_instructions}
    """

DANGER_MENU_CONTEXT = """
    제공된 마진 등급 위험 메뉴 데이터를 기반으로 개선 가이드를 작성해주세요. 행동 가이드는 무조건 2가지 액션 중 하나로 제공해주세요. 
    1. 해당 메뉴를 판매 대상에서 제외하거나 메뉴판 하단에 넣어 보조 메뉴 등으로 전환
    2. 권장가격 이상으로 가격을 조정 
    문장은 자연스럽게 바꾸어 제시해주세요.
    """
CAUTION_MENUS_CONTEXT = """
    제공된 마진 등급 주의 메뉴들의 데이터들을 기반으로 종합 개선 가이드를 작성해주세요. 행동 가이드는 무조건 2가지 액션 중 하나로 제공해주세요.
    1. 주의 메뉴 중 가장 공헌이익이 낮은 메뉴 1개만 선택해, 이번 주에 ‘안전 단계’로 옮기는 걸 목표로 해보세요. 이번 주 공헌이익이 가장 낮은 메뉴는 (주의 메뉴 중 공헌이익 가장 낮은 메뉴명)이에요. 안전 단계로 옮기기 위해서 권장가격인 (권장 가격)원 이상으로 가격을 소폭 조정해보세요.
    2. 주의 메뉴 중 가장 공헌이익이 낮은 메뉴 1개만 선택해, 이번 주에 ‘안전 단계’로 옮기는 걸 목표로 해보세요. 이번 주 공헌이익이 가장 낮은 메뉴는 (주의 메뉴 중 공헌이익 가장 낮은 메뉴명)이에요. 안전 단계로 옮기기 위해서 레시피에서 체감 없는 재료 1가지 조정해볼 수 있어요.
    문장은 자연스럽게 바꾸어 제시해주세요.
    """
HIGH_MARGIN_MENUS_CONTEXT = "제공된 고마진 메뉴들의 데이터들을 기반으로 카페 수익성을 개선할 수 있는 종합 가이드를 작성해주세요. "

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

class HighMarginMenusChain:

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=1.0,
            max_output_tokens=2000,
            google_api_key=settings.GOOGLE_API_KEY 
        )        
        self.parser = PydanticOutputParser(pydantic_object=HighMarginStrategyResponse)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", get_high_margin_strategy_system_prompt(HIGH_MARGIN_MENUS_CONTEXT, self.parser)),
            ("human", """
            고마진_메뉴_개수:{high_margin_menu_count}
            고마진_메뉴_목록(메뉴명/마진율/공헌이익):{high_margin_menu_details}
            고마진_메뉴_기여도:△{delta_margin}p
            """)
        ])

        self.chain = self.prompt | self.llm | self.parser


danger_menu_chain = DangerMenuChain()
caution_menus_chain = CautionMenusChain()
high_margin_menus_chain = HighMarginMenusChain()