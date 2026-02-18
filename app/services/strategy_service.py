from sqlalchemy.orm import Session
from app.crud.menu import menu_crud
from app.crud.user import user_crud
from app.crud.insight import insight_crud
from app.models.catalog  import Menu
import logging
from app.schemas.prompt_data import DangerMenu, CautionMenu, HighMarginMenus
from app.util.calculator import calculate_high_margin_contribution
from langchain_core.runnables import RunnableParallel
from app.chain.DangerMenuStrategy import danger_menu_chain
from app.chain.CautionMenuStrategy import caution_menus_chain
from app.chain.HighMarginMenuStrategy import high_margin_menus_chain
from app.util.calculator import calculate_avg_margin_rate, calculate_avg_margin_rate_after_simulate, calculate_avg_cost_rate, calculate_avg_contribution_margin, calculate_avg_cost_rate_except_menu, calculate_contribution_margin, calculate_contribution_margin_after_selling_price_change
logger = logging.getLogger(__name__)

DANGER_STRATEGY_TEMPLATES = {
    "REMOVE_MENU": {
        "expected_effect": "해당 메뉴를 제외하면, 카페 전체 평균 원가율이 {cost_rate_improvement}%p 개선될 수 있어요. 위험 메뉴를 정리하면, 동일한 매출 수준에서도 전체 수익 구조가 더 안정적이게 변해요."
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

class StrategyService:

    def __init__(self, catalog_db: Session, user_db: Session, insight_db: Session):
        self.catalog_db = catalog_db
        self.user_db = user_db
        self.insight_db = insight_db
    
    """전략 생성 """
    async def create_strategy(self):
        users = user_crud.get_users(self.user_db)
        for user in users:
            logger.warning(f"전략 생성 시작 | user_id={user.user_id} | store_name={user.store.name}")
            continue
        
            try:
                menus = menu_crud.get_menus(self.catalog_db, user.user_id)

                """baseline 저장"""
                avg_margin_rate = calculate_avg_margin_rate(menus)
                avg_cost_rate = calculate_avg_cost_rate(menus)
                avg_contribution_margin = calculate_avg_contribution_margin(menus)
                baseline_data = {
                    'avg_margin_rate': avg_margin_rate,
                    'avg_cost_rate': avg_cost_rate,
                    'avg_contribution_margin': avg_contribution_margin
                }
                logger.warning(f"Baseline 데이터 계산 완료 | user_id={user.user_id} | data={baseline_data}")
                baseline_id = insight_crud.save_strategy_baseline(self.insight_db, baseline_data, user.user_id)
                
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
                    logger.warning(f"Danger Menu Parameter 준비 완료 | user_id={user.user_id} | menus={danger_menu_parameter}")
                    chains_to_run["danger"] = danger_menu_chain.chain
                    input_params.update({
                        "danger_menu_count": len(danger_menus),
                        "menu_details": str(danger_menu_parameter)
                    })

                if caution_menus:
                    caution_menu_parameter = CautionMenu(
                        caution_menus[0].menu_name,
                        caution_menus[0].selling_price,
                        [[
                            {
                                "ingredient_name": recipe.ingredient.ingredient_name,
                                "unit": recipe.ingredient.unit_code,
                                "unit_price": recipe.ingredient.current_unit_price,
                                "base_quantity": recipe.ingredient.unit.base_quantity,
                                "quantity": recipe.amount
                            }
                            for recipe in caution_menus[0].recipes
                        ]],
                        caution_menus[0].cost_rate,
                        caution_menus[0].contribution_margin,
                        caution_menus[0].recommended_price
                    )
                    logger.warning(f"Caution Menu Parameter 준비 완료 | user_id={user.user_id} | menu={caution_menu_parameter}")
                    chains_to_run["caution"] = caution_menus_chain.chain
                    input_params.update({
                        "caution_menus_count": len(caution_menus),
                        "lowest_caution_menu_details": str(caution_menu_parameter)
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
                    logger.warning(f"High Margin Menu Parameter 준비 완료 | user_id={user.user_id} | menus={high_margin_menu_parameter}")
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
                                type = strategy.strategy_type
                                expected_effect = ""
                                if(type == "REMOVE_MENU"):
                                    expected_effect = DANGER_STRATEGY_TEMPLATES["REMOVE_MENU"]["expected_effect"].format(
                                        cost_rate_improvement = f"{int(avg_cost_rate - calculate_avg_cost_rate_except_menu(menus, danger_menus[i].menu_id)):,}"
                                    )
                                elif (type == "ADJUST_PRICE"):
                                    contribution_improvement = calculate_contribution_margin_after_selling_price_change(
                                        user,
                                        danger_menus[i],
                                        new_selling_price=float(danger_menus[i].recommended_price)
                                    ) - float(danger_menus[i].contribution_margin)
                                    
                                    expected_effect = DANGER_STRATEGY_TEMPLATES["ADJUST_PRICE"]["expected_effect"].format(
                                        recommended_price=f"{int(danger_menus[i].recommended_price):,}",
                                        contribution_improvement=f"{int(contribution_improvement):,}",
                                    )
                                insight_crud.save_danger_menu_strategy(
                                    db=self.insight_db,
                                    baseline_id=baseline_id,
                                    insight={
                                        'summary': strategy.summary,
                                        'analysis_detail': strategy.analysis_detail,
                                        'action_guide': strategy.action_guide,
                                        'expected_effect': expected_effect
                                    },
                                    menu_id=danger_menus[i].menu_id,
                                    type=type
                                )
                        logger.warning(f"위험 메뉴 전략 {len(danger_response.strategies)}개 저장 완료")
                        # logger.warning(result)

                    if 'caution' in result and result['caution']:
                        caution_response = result['caution']  
                        type = caution_response.strategy_type
                        
                        # 최저 공헌이익 메뉴
                        lowest_menu = caution_menus[0]
                        
                        if type == "ADJUST_PRICE":
                            price_gap = float(lowest_menu.recommended_price - lowest_menu.selling_price)
                            
                            expected_effect = CAUTION_STRATEGY_TEMPLATES["ADJUST_PRICE"]["expected_effect"].format(
                                recommended_price=f"{int(lowest_menu.recommended_price):,}",
                                contribution_improvement=f"{int(price_gap):,}"
                            )
                            
                        elif type == "ADJUST_RECIPE":
                            simulated_margin = calculate_avg_margin_rate_after_simulate(
                                selling_price=lowest_menu.selling_price,
                                current_cost_rate=lowest_menu.cost_rate,
                                current_margin_rate=lowest_menu.margin_rate
                            )
                            margin_improvement = float(simulated_margin) - float(avg_margin_rate)
                            
                            expected_effect = CAUTION_STRATEGY_TEMPLATES["ADJUST_RECIPE"]["expected_effect"].format(
                                margin_rate_improvement=f"{int(margin_improvement):,}"
                            )
                        
                        insight_crud.save_caution_menu_strategy(
                            db=self.insight_db,
                            baseline_id=baseline_id,
                            insight={
                                'summary': caution_response.summary,
                                'analysis_detail': caution_response.analysis_detail,
                                'action_guide': caution_response.action_guide,
                                'expected_effect': expected_effect
                            },
                            menu_id=caution_menus[0].menu_id,
                            type=type
                        )
                        logger.warning(f"주의 메뉴 전략 저장 완료")
                        logger.warning(result)

                    if 'high_margin' in result and result['high_margin']:
                        high_margin_response = result['high_margin']  
                        insight_crud.save_high_margin_menu_strategy(
                            db=self.insight_db,
                            baseline_id=baseline_id,
                            insight={
                                'summary': high_margin_response.summary,
                                'analysis_detail': high_margin_response.analysis_detail,
                                'action_guide': high_margin_response.action_guide,
                                'expected_effect': high_margin_response.expected_effect,
                                'completion_phrase': high_margin_response.completion_phrase
                            }
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
        danger_menus.sort(key=lambda x: -float(x.contribution_margin))
        return danger_menus[:5]

    def filter_caution_menus(self, menus: list[Menu]) -> list[Menu]:
        caution_menus = []
        for menu in menus:
            if menu.margin_grade_code == 'CAUTION':
                caution_menus.append(menu)
        caution_menus.sort(key=lambda x: -float(x.contribution_margin))
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