from schemas.guide import DangerMenu, CautionMenus, HighMarginMenus

class PromptGenerator:
    @staticmethod
    def generate_danger_strategy_system_prompt():

        promt = (
            f"""
            당신은 카페 운영자의 수익성 개선을 위한 전략 가이드를 작성하는 전문가입니다.
            아래 메뉴 데이터를 기반으로 마진 등급 위험 전략 가이드를 작성해주세요.

            [작성 규칙]
            1. 아래 키 구조로만 응답해주세요. 키 밖의 추가 텍스트는 작성하지 마세요.
            2. 각 키의 값은 메뉴 데이터를 참고하여 '~요'체로 자연스럽게 작성해주세요.
            3. 수치는 반드시 제공된 데이터 기준으로만 사용해주세요.
            4. 톤은 친절하고 부담 없이 조언하는 형태로 작성해주세요.

            [길이 가이드]
            summary: 1줄
            analysis_detail: 1~3줄
            action_guide: 1~2줄
            expected_effect: 1~2줄
            completion_phrase: 1~2줄

            [작성 포맷]
            summary:
            analysis_detail:
            action_guide:
            expected_effect:
            completion_phrase:
            """
            )
        return promt

    @staticmethod
    def generate_danger_strategy_user_prompt(menu: DangerMenu):
        
        ingredients=", ".join([f"{ing['ingredient_name']}/{ing['unit_price']}({ing['base_quantity']}{ing['unit']})/{ing['quantity']}" for ing in menu.ingredients])
        
        promt = (
            f"""
            카페명:{menu.cafe_name}
            메뉴명:{menu.menu_name}
            판매가격:{menu.selling_price}
            재료(재료명/단가/사용량):{ingredients}
            원가율:{menu.cost_rate}%
            공헌이익:{menu.contribution_margin}%
            권장가격:{menu.recommended_price}원
            """
            )
        return promt



    @staticmethod
    def generate_caution_strategy_system_prompt():

        promt = (
            f"""
            당신은 카페 운영자의 수익성 개선을 위한 전략 가이드를 작성하는 전문가입니다.
            아래 메뉴 데이터를 종합하여 단 하나의 마진 등급 주의 전략 가이드를 작성해주세요.

            [작성 규칙]
            1. 아래 키 구조로만 응답해주세요. 키 밖의 추가 텍스트는 작성하지 마세요.
            2. 각 키의 값은 메뉴 데이터를 참고하여 '~요'체로 자연스럽게 작성해주세요.
            3. 수치는 반드시 제공된 데이터 기준으로만 사용해주세요.
            4. 톤은 친절하고 부담 없이 조언하는 형태로 작성해주세요.

            [길이 가이드]
            summary: 1줄
            analysis_detail: 1~3줄
            action_guide: 1~2줄
            expected_effect: 1~2줄
            completion_phrase: 1~2줄

            [작성 포맷]
            summary: 1줄
            analysis_detail: 1~3줄
            action_guide: 1~2줄
            expected_effect: 1~2줄
            completion_phrase: 1~2줄
            """
            )
        return promt

    @staticmethod
    def generate_caution_strategy_user_prompt(menus: CautionMenus):
        caution_menu_details = ", ".join([f"{menu['menu_name']}/{menu['cost_rate']}/{menu['contribution_margin']}" for menu in menus.caution_menu_list])
        
        promt = (
            f"""
            [user]
            카페명:{menus.cafe_name}
            주의_메뉴_개수:{menus.caution_menu_count}
            주의_메뉴_목록(메뉴명/원가율/공헌이익):{caution_menu_details}
            최저_공헌이익_메뉴:{menus.lowest_contribution_menu_name} (공헌이익: {menus.lowest_contribuition_menu_margin}%)
            """
            )
        return promt



    @staticmethod
    def generate_high_margin_strategy_system_prompt():
    
        promt = (
            f"""
            당신은 카페 운영자의 수익성 개선을 위한 전략 가이드를 작성하는 전문가입니다.
            아래 메뉴 데이터를 종합하여 단 하나의 고마진 메뉴 전략 가이드를 작성해주세요.

            [작성 규칙]
            1. 아래 키 구조로만 응답해주세요. 키 밖의 추가 텍스트는 작성하지 마세요.
            2. 각 키의 값은 메뉴 데이터를 참고하여 '~요'체로 자연스럽게 작성해주세요.
            3. 수치는 반드시 제공된 데이터 기준으로만 사용해주세요.
            4. 톤은 친절하고 부담 없이 조언하는 형태로 작성해주세요.

            [길이 가이드]
            summary: 1줄
            analysis_detail: 1~3줄
            action_guide: 1~2줄
            expected_effect: 1~2줄
            completion_phrase: 1~2줄

            [작성 포맷]
            summary: 1줄
            analysis_detail: 1~3줄
            action_guide: 1~2줄
            expected_effect: 1~2줄
            completion_phrase: 1~2줄
            """
            )
        return promt

    @staticmethod
    def generate_high_margin_strategy_user_prompt(menus: HighMarginMenus):
        high_margin_menu_details = ", ".join([f"{menu['menu_name']}/{menu['margin_rate']}/{menu['contribution_margin']}" for menu in menus.high_margin_menu_list])
        
        promt = (
            f"""
            카페명:{menus.cafe_name}
            고마진_메뉴_개수:{menus.high_margin_menu_count}
            고마진_메뉴_목록(메뉴명/마진율/공헌이익):{high_margin_menu_details}
            고마진_메뉴_기여도:△{menus.delta_margin}p
            """
            )
        return promt