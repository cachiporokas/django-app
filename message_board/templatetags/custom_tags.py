from atexit import register
from django import template

register = template.Library()

@register.simple_tag(name='define')
def define(val=None):
  return val