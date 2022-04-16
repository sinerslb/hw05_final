# posts/tests/tests_form.py
import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя, автора тестового поста
        cls.auth = User.objects.create_user(username='auth')
        # Создадим записи в БД для проверки доступности адресов
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.new_test_group = Group.objects.create(
            title='Тестовая группа для замены в редактируемом посте',
            slug='test-slug2',
            description='Новое тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый пост о разном',
            group=cls.test_group,
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент, не имеющий отношения к посту
        self.user = User.objects.create_user(username='User')
        self.not_author_client = Client()
        self.not_author_client.force_login(self.user)
        # Создаем авторизованный клиент автора поста
        self.author_client = Client()
        self.author_client.force_login(self.auth)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.new_uploaded = SimpleUploadedFile(
            name='new_small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.form_data = {
            'text': 'Тестовый текст',
            'group': self.test_group.id,
            'image': self.uploaded,
        }
        self.new_form_data = {
            'text': 'Изменённый тестовый текст',
            'group': self.new_test_group.id,
            'image': self.new_uploaded,
        }
        self.post_count = Post.objects.count()

    def test_not_autorized_user_cant_create_post(self):
        """Неавторизованный пользователь не может создать запись."""
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, '/auth/login/?next=/create/')
        # Проверяем, что количество постов осталось прежним
        self.assertEqual(Post.objects.count(), self.post_count)

    def test_create_post_autorized_user(self):
        """Валидная форма создает запись в Post."""
        # Отправляем POST-запрос, пользователь авторизован
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.auth.username}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), self.post_count + 1)
        # Проверяем, что создалась запись с нужным содержимым
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.test_group.id,
                author=self.auth.id,
                image='posts/small.gif',
            ).exists()
        )

    def test_not_autorized_user_cant_edit_post(self):
        """Неавторизованный пользователь не может редактировать записи."""
        # Отправляем POST-запрос, пользователь не авторизован
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=self.new_form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')
        # Проверяем изменения в редактируемом посте
        self.assertFalse(
            Post.objects.filter(
                id=self.post.id,
                text='Изменённый тестовый текст',
                created=self.post.created,
                author=self.auth.id,
                group=self.new_test_group.id,
                image='posts/new_small.gif'
            ).exists()
        )

    def test_autorized_user_cant_edit_non_self_post(self):
        """Авторизованный пользователь не может редактировать чужие записи."""

        response = self.not_author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=self.new_form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        # Проверяем изменения в редактируемом посте
        self.assertFalse(
            Post.objects.filter(
                id=self.post.id,
                text='Изменённый тестовый текст',
                created=self.post.created,
                author=self.auth.id,
                group=self.new_test_group.id,
                image='posts/new_small.gif'
            ).exists()
        )

    def test_author_can_edit_post(self):
        """Автор может редактировать свои посты."""

        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=self.new_form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        # Проверяем, не увеличилось ли число постов
        self.assertEqual(Post.objects.count(), self.post_count)
        # Проверяем изменения в редактируемом посте
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text='Изменённый тестовый текст',
                created=self.post.created,
                author=self.auth.id,
                group=self.new_test_group.id,
                image='posts/new_small.gif'
            ).exists()
        )
