from django import template

register = template.Library()

@register.filter
def until(value, end):
    """
    使用例: {% for i in some_number|until:17 %}
    value から end-1 までの range を返す
    """
    try:
        return range(value, int(end))
    except:
        return []
