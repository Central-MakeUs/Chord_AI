from langchain_openai import ChatOpenAI
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
    2. 모든 답변은 '~해요', '~이에요/예요'와 같은 해요체(말 끝에 '요'를 붙이는 문체)를 사용해 주세요. 격식 있는 '하십시오체'나 딱딱한 말투는 피해 주세요. 특수기호는 사용하지 마세요
    3. 수치는 반드시 제공된 데이터 기준으로만 사용하되, 숫자는 모두 정수 형태(반올림)로 나타내주세요
    4. 추상적이지 않고 구체적인 행동 가이드를 작성해주세요

    [작성 가이드]
    {context}

    {format_instructions}
    """
HIGH_MARGIN_MENUS_CONTEXT = "제공된 고마진 메뉴들의 데이터들을 기반으로 카페 수익성을 개선할 수 있는 종합 가이드를 작성해주세요. "

class HighMarginMenusChain:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=1.0,
            max_tokens=2000,
            api_key=settings.OPENAI_API_KEY
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