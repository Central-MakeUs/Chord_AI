import logging
from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import settings
from crud.user import user_crud
from crud.menu import menu_crud
from crud.insight import insight_crud
from models.catalog_models import Menu
from models.user_models import Users
from util.prompt_generator import PromptGenerator
from schemas.guide import DangerMenu, CautionMenus, HighMarginMenus
from util.parser import parse_guide
from util.calculator import calculate_high_margin_contribution

logger = logging.getLogger(__name__)

client = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=1.0,
    max_output_tokens=2000,
    google_api_key=settings.GOOGLE_API_KEY 
)


async def run_guide_pipeline(catalog_db: Session, user_db: Session, insight_db: Session):
    users = user_crud.get_users(user_db)
    for user in users:
        try:
            
            menus = menu_crud.get_menus(catalog_db, user.user_id)

            # 위험 메뉴 가이드 생성
            await generate_danger_guides(catalog_db, insight_db, user, filter_danger_menus(menus))

            # 주의 메뉴 가이드 생성
            await generate_caution_guides(catalog_db, insight_db, user, filter_caution_menus(menus))

            # 고마진 메뉴 가이드 생성
            await generate_high_margin_guides(catalog_db, insight_db, user, menus)

            insight_db.commit()
            logger.info(f"파이프라인 성공 | user_id={user.user_id}")

        except Exception as e:
            insight_db.rollback()
            logger.error(f"가이드 생성 파이프라인 실패 | user_id={user.user_id} | error={str(e)}")
            continue

def filter_danger_menus(menus: list[Menu]) -> list[Menu]:
    danger_menus = []
    for menu in menus:
        if menu.margin_grade_code == 'DANGER':
            danger_menus.append(menu)
    return danger_menus

def filter_caution_menus(menus: list[Menu]) -> list[Menu]:
    caution_menus = []
    for menu in menus:
        if menu.margin_grade_code == 'CAUTION':
            caution_menus.append(menu)
    return caution_menus

def filter_high_margin_menus(menus: list[Menu]) -> list[Menu]:
    if not menus:
        return []

    contributions = [float(menu.contribution_margin) for menu in menus] 

    margin_average = sum(contributions) / len(contributions)
    margin_median = sorted(contributions)[len(contributions) // 2]

    high_margin_menus = [
        menu for menu, contrib in zip(menus, contributions)
        if contrib >= margin_average and contrib >= margin_median
    ]

    return sorted(high_margin_menus, key=lambda x: float(x.contribution_margin), reverse=True)[:5]

# 위험 메뉴 가이드 생성
async def generate_danger_guides(catalog_db: Session, insight_db: Session, user: Users, danger_menus: list[Menu]):
    if not danger_menus:
        logger.info(f"위험 메뉴 없음 | user_id={user.user_id}")
        return

    system_prompt = PromptGenerator.generate_danger_strategy_system_prompt()

    for menu in danger_menus:
        try:
            ingredients = [
                {
                    "ingredient_name": recipe.ingredient.ingredient_name,
                    "unit": recipe.ingredient.unit_code,
                    "unit_price": recipe.ingredient.current_unit_price,
                    "base_quantity": recipe.ingredient.unit.base_quantity,
                    "quantity": recipe.amount
                }
                for recipe in menu.recipes
            ]

            danger_menu = DangerMenu(
                user.store.name,
                menu.menu_name,
                menu.selling_price,
                ingredients,
                menu.cost_rate,
                menu.contribution_margin,
                menu.recommended_price
            )

            user_prompt = PromptGenerator.generate_danger_strategy_user_prompt(danger_menu)

            guide_content = await call_llm(system_prompt, user_prompt)

            parsed = parse_guide(guide_content)

            insight_crud.save_danger_menu_strategy(insight_db, parsed, menu.menu_id)

            logger.info(f"위험 메뉴 가이드 생성 성공 | user_id={user.user_id} | menu_id={menu.menu_id}")
            logger.info("---llm response--")
            logger.info(f"요약:{parsed['summary']}")
            logger.info(f"상세:{parsed['analysis_detail']}")
            logger.info(f"행동 가이드:{parsed['action_guide']}")
            logger.info(f"기대효과:{parsed['expected_effect']}")
            logger.info(f"완료 멘트:{parsed['completion_phrase']}")

        except Exception as e:
            logger.error(f"위험 메뉴 가이드 생성 실패 | user_id={user.user_id} | menu_id={menu.menu_id} | error={str(e)}")
            continue


# 주의 메뉴 가이드 생성
async def generate_caution_guides(catalog_db: Session, insight_db: Session, user: Users, caution_menus: list[Menu]):
    if not caution_menus:
        logger.info(f"주의 메뉴 없음 | user_id={user.user_id}")
        return

    try:
        system_prompt = PromptGenerator.generate_caution_strategy_system_prompt()

        caution_menu_list = [
            {
                "menu_name": menu.menu_name,
                "cost_rate": menu.cost_rate,
                "contribution_margin": menu.contribution_margin
            }
            for menu in caution_menus
        ]

        menus = CautionMenus(
            user.store.name,
            len(caution_menus),
            caution_menu_list,
            min(caution_menus, key=lambda x: x.contribution_margin).menu_name,
            min(caution_menus, key=lambda x: x.contribution_margin).contribution_margin
        )

        user_prompt = PromptGenerator.generate_caution_strategy_user_prompt(menus)

        guide_content = await call_llm(system_prompt, user_prompt)

        parsed = parse_guide(guide_content)

        insight_crud.save_caution_menu_strategy(insight_db, parsed, user.user_id)

        logger.info(f"주의 메뉴 가이드 생성 성공 | user_id={user.user_id}")
        logger.info("---llm response--")
        logger.info(f"요약:{parsed['summary']}")
        logger.info(f"상세:{parsed['analysis_detail']}")
        logger.info(f"행동 가이드:{parsed['action_guide']}")
        logger.info(f"기대효과:{parsed['expected_effect']}")
        logger.info(f"완료 멘트:{parsed['completion_phrase']}")

    except Exception as e:
        logger.error(f"주의 메뉴 가이드 생성 실패 | user_id={user.user_id} | error={str(e)}")


# 고마진 메뉴 가이드 생성
async def generate_high_margin_guides(catalog_db: Session, insight_db: Session, user: Users, all_menus: list[Menu]):
    high_margin_menus = filter_high_margin_menus(all_menus)

    if not high_margin_menus:
        logger.info(f"고마진 메뉴 없음 | user_id={user.user_id}")
        return

    try:
        system_prompt = PromptGenerator.generate_high_margin_strategy_system_prompt()

        high_margin_menu_list = [
            {
                "menu_name": menu.menu_name,
                "margin_rate": menu.margin_rate,
                "contribution_margin": menu.contribution_margin
            }
            for menu in high_margin_menus
        ]

        menus = HighMarginMenus(
            user.store.name,
            len(high_margin_menus),
            high_margin_menu_list,
            calculate_high_margin_contribution(all_menus, high_margin_menus)
        )

        user_prompt = PromptGenerator.generate_high_margin_strategy_user_prompt(menus)

        guide_content = await call_llm(system_prompt, user_prompt)

        parsed = parse_guide(guide_content)

        insight_crud.save_high_margin_menu_strategy(insight_db, parsed, user.user_id)

        logger.info(f"고마진 메뉴 가이드 생성 성공 | user_id={user.user_id}")
        logger.info("---llm response--")
        logger.info(f"요약:{parsed['summary']}")
        logger.info(f"상세:{parsed['analysis_detail']}")
        logger.info(f"행동 가이드:{parsed['action_guide']}")
        logger.info(f"기대효과:{parsed['expected_effect']}")
        logger.info(f"완료 멘트:{parsed['completion_phrase']}")

    except Exception as e:
        logger.error(f"고마진 메뉴 가이드 생성 실패 | user_id={user.user_id} | error={str(e)}")

async def call_llm(system_prompt: str, user_prompt: str) -> str:
    response = await client.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    print(response.content)
    return response.content