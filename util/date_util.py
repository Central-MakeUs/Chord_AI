from datetime import datetime, timedelta

"""다음 주 월요일 날짜 반환"""
def get_next_monday() -> datetime.date:
    today = datetime.now().date()
    days_ahead = 7 - today.weekday()
    
    if days_ahead <= 0:  
        days_ahead += 7
    
    next_monday = today + timedelta(days=days_ahead)
    return next_monday