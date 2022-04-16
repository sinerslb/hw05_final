# posts/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост о разном',
        )

    def setUp(self):
        self.posts_post = PostModelTest.post

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        posts_group = PostModelTest.group
        posts_post_str = self.posts_post.__str__()
        posts_group_str = posts_group.__str__()
        self.assertEqual(posts_post_str, self.post.text[:15])
        self.assertEqual(posts_group_str, self.group.title)

    def test_verbose_name(self):
        """Проверяем verbose_name у полей моделей."""
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.posts_post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """Проверяем help_text у полей моделей."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите изображение',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.posts_post._meta.get_field(field).help_text,
                    expected_value
                )
