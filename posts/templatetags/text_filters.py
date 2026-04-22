from django import template
from django.utils.safestring import mark_safe

from common.markdown.markdown import markdown_comment

register = template.Library()


@register.filter(is_safe=True)
def markdown(text):
    return mark_safe(markdown_comment(text))


@register.filter
def rupluralize(value, arg="дурак,дурака,дураков"):
    args = arg.split(",")
    number = abs(int(value))
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return args[0]
    elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
        return args[1]
    else:
        return args[2]
