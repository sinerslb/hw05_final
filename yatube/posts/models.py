# posts/models.py
from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    """Модель групп."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    """Модель постов."""

    text = models.TextField('Текст поста',
                            help_text='Введите текст поста'
                            )

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор',
                               )

    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text=('Группа, к которой будет относиться '
                                         'пост'),
                              )

    image = models.ImageField('Изображение',
                              upload_to='posts/',
                              blank=True,
                              help_text=('Загрузите изображение'),
                              )

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return self.text[:15]


class Comment(CreatedModel):
    """Модель комментариев."""

    post = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE,
                             )

    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE,
                               )

    text = models.TextField('Текст комментария',
                            help_text='Введите текст комментария'
                            )


class Follow(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE,
                             )

    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE,
                               )
