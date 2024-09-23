from django import template

from game.models import TagPost

register = template.Library()


@register.inclusion_tag('game/list_tags.html')
def show_tags():
    return {'tags':TagPost.objects.all()}