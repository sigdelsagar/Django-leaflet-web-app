from django import template

register = template.Library()

@register.simple_tag
def set(val=0):
    return val
