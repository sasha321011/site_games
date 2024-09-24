from django import template

from game.models import TagPost

register = template.Library()


@register.inclusion_tag('game/list_tags.html')
def show_tags():
    return {'tags':TagPost.objects.all()}


@register.simple_tag
def url_replace(request, field, value):
    """Заменяет или добавляет параметры GET запроса."""
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
