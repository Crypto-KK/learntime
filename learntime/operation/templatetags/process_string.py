import re

from django import template

register = template.Library()


@register.filter
def removeHTML100(value):
    dr = re.compile(r'<[^>]+>', re.S)
    dd = dr.sub('', value)
    return dd[:100] + '...'
