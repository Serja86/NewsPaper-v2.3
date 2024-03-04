from datetime import datetime

from django import template
from .models import *

register = template.Library()


# @register.simple_tag()
# def current_time(format_string='%b %d %Y'):
#    return datetime.utcnow().strftime(format_string)
#
# @register.simple_tag(takes_context=True)
# def url_replace(context, **kwargs):
#    d = context['request'].GET.copy()
#    for k, v in kwargs.items():
#        d[k] = v
#    return d.urlencode()

@register.simple_tag(name='getcats')
def get_categories(filter=None):
    if not filter:
        return Category.objects.all()
    else:
        return Category.objects.filter(pk=filter)


@register.inclusion_tag('news/list_categories.html')
def show_categories(sort=None, cat_selected=0):
    if not sort:
        cats = Category.objects.all()
    else:
        cats = Category.objects.order_by(sort)

    return {'cats': cats, 'cat_selected': cat_selected}