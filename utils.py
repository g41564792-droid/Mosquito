from datetime import datetime

# Проверка допустимых размеров
def validate_size(width, height):
    if not (150 <= width <= 3000) or not (150 <= height <= 3000):
        return {"valid": False, "msg": "Размер изделия должен быть от 150 мм до 3000 мм."}
    
    # Проверка необходимости импоста
    needs_impost = (width > 1200) or (height > 1200)
    if needs_impost:
        return {"valid": True, "needs_impost": True, "msg": "Рекомендуется установка импоста."}
    return {"valid": True, "needs_impost": False}

def validate_quantity(qty):
    if qty > 30:
        return {"valid": False, "msg": "Максимум 30 единиц. Для большого объема свяжитесь с менеджером."}
    return {"valid": True}