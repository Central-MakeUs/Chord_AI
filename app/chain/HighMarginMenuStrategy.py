from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.chain.response_schema import HighMarginStrategyResponse
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

def get_system_prompt(context: str, parser: PydanticOutputParser) -> str:
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
HIGH_MARGIN_MENUS_CONTEXT = "제공된 고마진 메뉴들의 데이터들을 기반으로 카페 수익성을 개선할 수 있는 종합 가이드를 작성해주세요. "

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
            ("system", get_system_prompt(HIGH_MARGIN_MENUS_CONTEXT, self.parser)),
            ("human", """
            고마진_메뉴_개수:{high_margin_menu_count}
            고마진_메뉴_목록(메뉴명/마진율/공헌이익):{high_margin_menu_details}
            고마진_메뉴_기여도:△{delta_margin}p
            """)
        ])

        self.chain = self.prompt | self.llm | self.parser

high_margin_menus_chain = HighMarginMenusChain()