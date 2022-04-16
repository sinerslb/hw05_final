# posts/tests/test_views.py
import shutil
import tempfile
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post, Comment
from posts.views import POST_COUNT

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим записи в БД для проверки доступности адресов
        cls.auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа №1',
            slug='test-slug1',
            description='Тестовое описание №1',
        )
        # картинка для теста
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый пост о разном',
            group=cls.group,
            image=uploaded,
        )
        Comment.objects.create(
            post=cls.post,
            author=cls.auth,
            text='Тестовый коммент',
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем не авторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth)
        cache.clear()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """Тест пространства имён, URL-адрес использует соответствующий шаблон.
        """
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_page', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.auth.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страниц index, group_list и profile
    # в первом элементе списка object_list содержат ожидаемые значения
    def test_index_group_profile_pages_show_correct_context(self):
        """Шаблоны страниц index, group_list и profile сформированы
        с правильным контекстом.
        """

        names_pages = [
            reverse('posts:index'),
            reverse('posts:group_page', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.auth.username}),
        ]
        for reverse_name in names_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                text_0 = first_object.text
                created_0 = first_object.created
                author_0 = first_object.author
                group_0 = first_object.group
                id_0 = first_object.id
                image_0 = first_object.image

                self.assertEqual(
                    text_0, self.post.text,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    created_0, self.post.created,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    author_0, self.auth,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    group_0, self.group,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    id_0, self.post.id,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    image_0, self.post.image,
                    'Ошибка словаря context на странице: ' + reverse_name)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').created,
                         self.post.created)
        self.assertEqual(response.context.get('post').author,
                         self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_create_comments_not_authorized_users(self):
        """Неавторизованный пользователь не может оставлять комментарии"""
        comment_data = {
            'post': self.post.id,
            'author': self.auth.id,
            'text': 'Новый тестовый коммент',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_data,
            follow=True,
        )
        self.assertFalse(
            Comment.objects.filter(text='Новый тестовый коммент').exists()
        )

    def test_create_comments_authorized_users(self):
        """После успешной отправки комментарий появляется на странице поста."""
        comment_data = {
            'post': self.post.id,
            'author': self.auth.id,
            'text': 'Новый тестовый коммент',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_data,
            follow=True,
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        comment = response.context['comments'][1]
        self.assertEqual(comment.text, 'Новый тестовый коммент')

    # Проверка словаря контекста страницы редактирования поста
    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Проверка словаря контекста страницы создания поста
    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Проверка кеширования на главной странице."""
        Post.objects.create(
            author=self.auth,
            text='Проверка кеширования',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        before_delete_post = response.content
        Post.objects.filter(text='Проверка кеширования').delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(before_delete_post, response.content)


class TestPaginatorAndFiltration(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим записи в БД для проверки количества постов на страницах
        # Создаем авторов постов
        cls.auth = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='user')
        # Создаем группы
        cls.group_1 = Group.objects.create(
            title='Тестовая группа №1',
            slug='test-slug1',
            description='Тестовое описание №1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа №2',
            slug='test-slug2',
            description='Тестовое описание №2',
        )
        # Создаём посты
        for i in range(16):
            if i < 5:
                Post.objects.create(
                    author=cls.user,
                    text='Тестовый пост о разном' + str(i),
                    group=cls.group_1,
                )
            else:
                Post.objects.create(
                    author=cls.auth,
                    text='Тестовый пост о разном' + str(i),
                    group=cls.group_2,
                )
        # Пост для тестирования фильтрации
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост для тестирования фильтрации',
            group=cls.group_2,
        )

    def setUp(self):
        # Создаем клиент
        self.client = Client()

    def test_pages_contains_POST_COUNT_records(self):
        '''Проверка ожидаемого количества постов на страницах.'''
        # Словарь "имя_html_шаблона: reverse(name)":
        # ожидаемое число постов на второй странице
        page_2_index_cnt = Post.objects.all().count() % POST_COUNT
        page_2_group_cnt = (Post.objects.filter(group=self.group_2.id).count()
                            % POST_COUNT)
        page_2_author_cnt = (Post.objects.filter(author=self.auth.id).count()
                             % POST_COUNT)
        templates_pages_names = {
            reverse('posts:index'): page_2_index_cnt,
            reverse('posts:group_page',
                    kwargs={'slug': self.group_2.slug}): page_2_group_cnt,
            reverse('posts:profile',
                    kwargs={'username': self.auth.username}):
                        page_2_author_cnt,
        }

        for reverse_name, page_2_posts_count in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                # Проверка: количество постов на первой странице
                # равно POST_COUNT.
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), POST_COUNT,
                    f'{reverse_name} содержит не {POST_COUNT} постов'
                )
                # Проверка: количество оставшихся постов на второй странице.
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), page_2_posts_count,
                    f'Вторая страница {reverse_name}'
                    f' содержит не {page_2_posts_count} постов'
                )

    def test_post_not_in_wrong_group(self):
        """Проверка отсутсвия поста в группе, к которой он не относится."""
        response = self.client.get(
            reverse('posts:group_page', kwargs={'slug': self.group_1.slug})
        )
        self.assertContains(response, self.post.text, 0)

    def test_post_not_in_wrong_author(self):
        """Проверка отсутсвия поста нас странице автора,
        которому пост не принадлежит.
        """
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.auth.username})
        )
        self.assertContains(response, self.post.text, 0)


class TestFollowing(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.author = User.objects.create_user(username='author')
        cls.not_follower = User.objects.create_user(username='not_follower')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Привет подписчики!',
        )

    def setUp(self) -> None:
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        cache.clear()

    def test_create_delete_follow(self):
        """Проверка возможности подписки/отписки для авторизованного
        пользователя.
        """
        self.follower_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}),
            follow=True,
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower, author=self.author
            ).exists(),
            'Подписки не создаются'
        )

        self.follower_client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username}),
            follow=True,
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower, author=self.author
            ).exists(),
            'Подписки не удаляются'
        )

    def test_followers_see_post(self):
        """Проверка, подписанные пользователи видят посты авторов"""
        Follow.objects.create(
            user=self.follower,
            author=self.author,
        )
        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.context.get('post').text,
                         'Привет подписчики!')

    def test_not_followers_dont_see_post(self):
        """Проверка, неподписанные пользователи не видят посты авторов"""
        not_follower_client = Client()
        not_follower_client.force_login(self.follower)
        response = not_follower_client.get(reverse('posts:follow_index'))
        self.assertFalse(response.context.get('post'))
