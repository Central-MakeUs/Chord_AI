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