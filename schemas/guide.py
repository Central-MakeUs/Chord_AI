from dataclasses import dataclass

@dataclass
class DangerMenu:
    cafe_name: str
    menu_name: str
    selling_price: float
    ingredients: list                         #(ingredient_name: str, unit: str, unit_price: float, base_quantity: float, quantity: float)
    cost_rate: float
    contribution_margin: float
    recommended_price: float

@dataclass
class CautionMenus:
    cafe_name: str
    caution_menu_count: int
    caution_menu_list: list                  #(menu_name: str, cost_rate: float, contribution_margin: float)
    lowest_contribution_menu_name: str 
    lowest_contribuition_menu_margin: float

@dataclass
class HighMarginMenus:
    cafe_name: str
    high_margin_menu_count: int
    high_margin_menu_list: list             #(menu_name: str, margin_rate: float, contribution_margin: float)
    delta_margin: float