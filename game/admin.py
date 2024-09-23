from django.contrib import admin, messages

from .models import Game, TagPost


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    exclude = ['is_published']
    readonly_fields = ['slug']
    list_display = ('id', 'title', 'image', 'time_create', 'time_update', 'is_published', 'display_tags')
    list_display_links = ('id', 'title')
    ordering = ['time_create', 'title']
    list_editable = ('is_published',)
    filter_horizontal = ('tags',)
    actions = ['set_published']
    search_fields = ['title']
    list_filter = ['is_published']

    def display_tags(self, obj):
        return ", ".join([tag.tag for tag in obj.tags.all()])

    display_tags.short_description = 'Теги'

    def set_published(self, request, queryset):
        count = queryset.update(is_published=Game.Status.PUBLISHED)
        self.message_user(request, f"Edit:{count}")

    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Game.Status.DRAFT)
        self.message_user(request, f"Edit:{count}", messages.WARNING)


@admin.register(TagPost)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag')
    list_display_links = ('id', 'tag')
