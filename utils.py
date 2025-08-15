import random
from config import UNIQUE_RANGE
from db import get_open_amounts

def build_unique_amount(base_price_kzt: int) -> int:
    """Добавляет уникальный суффикс к цене, избегая коллизий с открытыми заказами."""
    busy = get_open_amounts()
    lo, hi = UNIQUE_RANGE
    candidates = list(range(base_price_kzt + lo, base_price_kzt + hi))
    random.shuffle(candidates)
    for val in candidates:
        if val not in busy:
            return val
    # если вдруг все заняты — крайний случай
    return base_price_kzt + random.randint(lo, hi)
