from django import template

register = template.Library()

@register.filter
def format_price(value):
    """Форматирует цену с разделителями тысяч"""
    try:
        # Конвертируем в число и форматируем
        price = int(float(value))
        return f"{price:,}".replace(',', ' ')
    except (ValueError, TypeError):
        return value 