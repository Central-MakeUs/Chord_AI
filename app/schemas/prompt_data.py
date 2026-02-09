from dataclasses import dataclass

@dataclass
class DangerMenu:
    menu_name: str
    selling_price: float
    ingredients: list                         #(ingredient_name: str, unit: str, unit_price: float, base_quantity: float, quantity: float)
    cost_rate: float
    contribution_margin: float
    recommended_price: float

@dataclass
class CautionMenu:
    caution_menu_name: str
    selling_price: float
    ingredients: list                         #(ingredient_name: str, unit: str, unit_price: float, base_quantity: float, quantity: float)
    cost_rate: float
    contribution_margin: float
    recommended_price: float

@dataclass
class HighMarginMenus:
    high_margin_menu_count: int
    high_margin_menu_list: list             #(menu_name: str, margin_rate: float, contribution_margin: float)
    delta_margin: float