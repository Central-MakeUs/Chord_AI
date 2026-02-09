from app.models.user import Users
from app.models.catalog import Menu
from decimal import Decimal

def calculate_high_margin_contribution(all_menus: list, high_margin_menus: list) -> float:
    """
    고마진 메뉴들이 카페 평균 마진율에 미치는 기여도 계산
    Returns: △마진율(%p)
    """
    total_count = len(all_menus)

    # 카페 평균 마진율
    M_avg = sum(m.margin_rate for m in all_menus) / total_count

    # 고마진 메뉴 실제 마진율 합
    high_margin_sum = sum(m.margin_rate for m in high_margin_menus)

    # 고마진 메뉴를 평균으로 대체한 가정의 마진율
    M_without_high = (sum(m.margin_rate for m in all_menus) - high_margin_sum + len(high_margin_menus) * M_avg) / total_count

    # 기여도
    delta = M_avg - M_without_high

    return round(delta, 1)

def calculate_avg_margin_rate(menus: list) -> float:
    """카페 평균 마진률 계산"""
    if not menus:
        return 0.0
    menus_num = len(menus)

    total_margin_rate = sum(float(menu.margin_rate) for menu in menus)
    avg_margin_rate = total_margin_rate / menus_num
    return round(avg_margin_rate, 2)

def calculate_avg_margin_rate_after_simulate(
    selling_price: Decimal,
    current_cost_rate: Decimal,
    current_margin_rate: Decimal,
    target_cost_rate: Decimal = Decimal('25.0')
) -> float:
    """전략 실행 시 예상되는 마진율 계산"""

    current_cost_rate = float(current_cost_rate)
    current_margin_rate = float(current_margin_rate)
    target_cost_rate = float(target_cost_rate)
    
    labor_cost_rate = 100.0 - current_cost_rate - current_margin_rate
    simulated_margin_rate = 100.0 - target_cost_rate - labor_cost_rate
    
    return round(simulated_margin_rate, 2)  

def calculate_avg_cost_rate(menus: list) -> float:
    """카페 평균 원가율 계산"""
    if not menus:
        return 0.0
    menus_num = len(menus)

    total_cost_rate = sum(float(menu.cost_rate) for menu in menus)
    avg_cost_rate = total_cost_rate / menus_num
    return round(avg_cost_rate, 2)

def calculate_avg_contribution_margin(menus: list) -> float:
    """카페 평균 기여마진 계산"""
    if not menus:
        return 0.0
    menus_num = len(menus)
    total_contribution_margin = sum(float(menu.contribution_margin) for menu in menus)
    avg_contribution_margin = total_contribution_margin / menus_num
    return round(avg_contribution_margin, 2)

def calculate_avg_cost_rate_except_menu(menus: list, except_menu_id: int) -> float:
    """특정 메뉴를 제외한 카페 평균 원가율 계산"""
    filtered_menus = [menu for menu in menus if menu.menu_id != except_menu_id]
    if not filtered_menus:
        return 0.0
    menus_num = len(filtered_menus)

    total_cost_rate = sum(float(menu.cost_rate) for menu in filtered_menus)
    avg_cost_rate = total_cost_rate / menus_num
    return round(avg_cost_rate, 2)

def calculate_contribution_margin(user: Users, menu: Menu) -> float:
    """공헌이익 계산"""
    labor_cost_per_cup = float(user.store.labor_cost) / 3600 * float(menu.work_time)
    
    total_cost = sum([
        float(recipe.ingredient.current_unit_price) * 
        (float(recipe.amount) / float(recipe.ingredient.unit.base_quantity))
        for recipe in menu.recipes
    ])
    
    contribution_margin = float(menu.selling_price) - (total_cost + labor_cost_per_cup)
    
    return round(contribution_margin, 2)



def calculate_contribution_margin_after_selling_price_change(user: Users, menu: Menu, new_selling_price: float) -> float:
    """판매가 변경 후 공헌이익 계산"""
    labor_cost_per_cup = float(user.store.labor_cost) / 3600 * float(menu.work_time)
    
    total_cost = sum([
        float(recipe.ingredient.current_unit_price) * 
        (float(recipe.amount) / float(recipe.ingredient.unit.base_quantity))
        for recipe in menu.recipes
    ])
    
    contribution_margin = float(new_selling_price) - (total_cost + labor_cost_per_cup)
    
    return round(contribution_margin, 2)