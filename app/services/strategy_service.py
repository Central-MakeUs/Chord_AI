from sqlalchemy.orm import Session
from app.crud.menu import menu_crud
from app.crud.user import user_crud
from app.crud.insight import insight_crud
from app.models.catalog  import Menu
import logging
from app.schemas.prompt_data import DangerMenu, CautionMenus, HighMarginMenus
from app.util.calculator import calculate_high_margin_contribution
from langchain_core.runnables import RunnableParallel
from app.chain.DangerMenuStrategy import danger_menu_chain
from app.chain.CautionMenuStrategy import caution_menus_chain
from app.chain.HighMarginMenuStrategy import high_margin_menus_chain

logger = logging.getLogger(__name__)

class StrategyService:

    def __init__(self, catalog_db: Session, user_db: Session, insight_db: Session):
        self.catalog_db = catalog_db
        self.user_db = user_db
        self.insight_db = insight_db
    
    """전략 생성 """
    async def create_strategy(self):
        users = user_crud.get_users(self.user_db)
        for user in users:
            try:
                menus = menu_crud.get_menus(self.catalog_db, user.user_id)
                
                """위험 메뉴"""
                danger_menus = self.filter_danger_menus(menus)[:5]

                """주의 메뉴"""
                caution_menus = self.filter_caution_menus(menus)

                """고마진 메뉴"""
                high_margin_menus = self.filter_high_margin_menus(menus)

                chains_to_run = {}
                input_params = {"cafe_name": user.store.name}

                if danger_menus:
                    danger_menu_parameter = [
                        DangerMenu(
                            menu.menu_name,
                            menu.selling_price,
                            [[
                                {
                                    "ingredient_name": recipe.ingredient.ingredient_name,
                                    "unit": recipe.ingredient.unit_code,
                                    "unit_price": recipe.ingredient.current_unit_price,
                                    "base_quantity": recipe.ingredient.unit.base_quantity,
                                    "quantity": recipe.amount
                                }
                                for recipe in menu.recipes
                            ]],
                            menu.cost_rate,
                            menu.contribution_margin,
                            menu.recommended_price
                        )
                        for menu in danger_menus
                    ]
                    chains_to_run["danger"] = danger_menu_chain.chain
                    input_params.update({
                        "danger_menu_count": len(danger_menus),
                        "menu_details": str(danger_menu_parameter)
                    })

                if caution_menus:
                    caution_menu_parameter = CautionMenus(
                        len(caution_menus),
                        [[
                            {
                                "menu_name": menu.menu_name,
                                "cost_rate": menu.cost_rate,
                                "contribution_margin": menu.contribution_margin
                            }
                            for menu in caution_menus
                        ]],
                        min(caution_menus, key=lambda x: x.contribution_margin).menu_name,
                        min(caution_menus, key=lambda x: x.contribution_margin).contribution_margin
                    )
                    chains_to_run["caution"] = caution_menus_chain.chain
                    input_params.update({
                        "caution_menu_count": caution_menu_parameter.caution_menu_count,
                        "caution_menu_details": str(caution_menu_parameter.caution_menu_list),
                        "lowest_contribution_menu_name": caution_menu_parameter.lowest_contribution_menu_name,
                        "lowest_contribuition_menu_margin": caution_menu_parameter.lowest_contribuition_menu_margin
                    })

                if high_margin_menus:
                    high_margin_menu_parameter = HighMarginMenus(
                        len(high_margin_menus),
                        [[
                            {
                                "menu_name": menu.menu_name,
                                "margin_rate": menu.margin_rate,
                                "contribution_margin": menu.contribution_margin
                            }
                            for menu in high_margin_menus
                        ]],
                        calculate_high_margin_contribution(menus, high_margin_menus)
                    )
                    chains_to_run["high_margin"] = high_margin_menus_chain.chain
                    input_params.update({
                        "high_margin_menu_count": high_margin_menu_parameter.high_margin_menu_count,
                        "high_margin_menu_details": str(high_margin_menu_parameter.high_margin_menu_list),
                        "delta_margin": high_margin_menu_parameter.delta_margin
                    })

                if chains_to_run:
                    parallel_chain = RunnableParallel(**chains_to_run)
                    result = parallel_chain.invoke(input_params)

                    # db 저장
                    if 'danger' in result and result['danger']:
                        danger_response = result['danger'] 
                        for i, strategy in enumerate(danger_response.strategies):
                            if i < len(danger_menus): 
                                insight_crud.save_danger_menu_strategy(
                                    db=self.insight_db,
                                    insight={
                                        'summary': strategy.summary,
                                        'analysis_detail': strategy.analysis_detail,
                                        'action_guide': strategy.action_guide,
                                        'expected_effect': "기대효과",
                                        'completion_phrase':"완료 문구"
                                    },
                                    menu_id=danger_menus[i].menu_id,
                                    user_id=user.user_id
                                )
                        logger.warning(f"위험 메뉴 전략 {len(danger_response.strategies)}개 저장 완료")
                        # logger.warning(result)

                    if 'caution' in result and result['caution']:
                        caution_response = result['caution']  
                        insight_crud.save_caution_menu_strategy(
                            db=self.insight_db,
                            insight={
                                'summary': caution_response.summary,
                                'analysis_detail': caution_response.analysis_detail,
                                'action_guide': caution_response.action_guide,
                                'expected_effect': "기대효과",
                                'completion_phrase':"완료 문구"
                            },
                            user_id=user.user_id
                        )
                        logger.warning(f"주의 메뉴 전략 저장 완료")
                        logger.warning(result)

                    if 'high_margin' in result and result['high_margin']:
                        high_margin_response = result['high_margin']  
                        insight_crud.save_high_margin_menu_strategy(
                            db=self.insight_db,
                            insight={
                                'summary': high_margin_response.summary,
                                'analysis_detail': high_margin_response.analysis_detail,
                                'action_guide': high_margin_response.action_guide,
                                'expected_effect': high_margin_response.expected_effect,
                                'completion_phrase': high_margin_response.completion_phrase
                            },
                            user_id=user.user_id
                        )
                        logger.warning(f"고마진 메뉴 전략 저장 완료")
                        # logger.warning(result)

                    self.insight_db.commit()

                    logger.warning(f"전략 생성 성공 | user_id={user.user_id} | chains={list(chains_to_run.keys())}")
                else:
                    logger.warning(f"전략 생성 스킵 | user_id={user.user_id} | 실행 가능한 메뉴 없음")

            except Exception as e:
                self.insight_db.rollback()
                logger.error(f"전략 생성 파이프라인 실패 | user_id={user.user_id} | error={str(e)}")
                continue
    
    def filter_danger_menus(self, menus: list[Menu]) -> list[Menu]:
        danger_menus = []
        for menu in menus:
            if menu.margin_grade_code == 'DANGER':
                danger_menus.append(menu)
        return danger_menus[:5]

    def filter_caution_menus(self, menus: list[Menu]) -> list[Menu]:
        caution_menus = []
        for menu in menus:
            if menu.margin_grade_code == 'CAUTION':
                caution_menus.append(menu)
        return caution_menus

    def filter_high_margin_menus(self, menus: list[Menu]) -> list[Menu]:
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