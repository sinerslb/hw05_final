# posts/admin.py
from django.contrib import admin
from django.utils.safestring import mark_safe
from posts.models import Group, Post, Comment, Follow


class PostAdmin(admin.ModelAdmin):

    list_display = ('pk',
                    'text',
                    'created',
                    'author',
                    'group',
                    'preview_image',
                    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    fields = (
        'text',
        'author',
        'group',
        'image',
        'preview_image',
    )
    readonly_fields = (
        'preview_image',
    )

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width=100>')

    preview_image.short_description = "Миниатюра"


class GroupAdmin(admin.ModelAdmin):

    list_display = ('pk',
                    'title',
                    'slug',
                    'description',
                    )
    empty_value_displey = '-пусто-'


class CommentAdmin(admin.ModelAdmin):

    list_display = ('pk',
                    'text',
                    'author',
                    'post',
                    )
    empty_value_displey = '-пусто-'


class FollowAdmin(admin.ModelAdmin):

    list_display = ('user',
                    'author',
                    )
    list_filter = ('user',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
