# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя, автора тестового поста
        cls.auth = User.objects.create_user(username='auth')
        # Создадим записи в БД для проверки доступности адресов
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый пост о разном',
        )
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем автора поста
        self.authorized_client.force_login(self.auth)

    def test_urls_uses_correct_template(self):
        """Проверка доступности страниц и использования правильных шаблонов.
        """
        # адрес, шаблон, ответ неавторизованному и авторизованному юзеру
        temp_url_names = [
            ('/', 'posts/index.html',
             200, 200
             ),
            ('/group/test-slug/', 'posts/group_list.html',
             200, 200
             ),
            ('/profile/HasNoName/', 'posts/profile.html',
             200, 200
             ),
            (f'/posts/{self.post.id}/', 'posts/post_detail.html',
             200, 200
             ),
            (f'/posts/{self.post.id}/edit/', 'posts/create_post.html',
             302, 200
             ),
            ('/create/', 'posts/create_post.html',
             302, 200
             ),
            ('/unexisting_page', '',
             404, 404
             ),
        ]
        for addr, templ, resp_n_login, resp_login in temp_url_names:
            with self.subTest(address=addr):
                # доступность страницы не авторизованному юзеру
                response = self.guest_client.get(addr)
                self.assertEqual(response.status_code, resp_n_login,
                                 addr + 'недоступна неавторизованному'
                                 ' пользователю')

                # доступность страницы авторизованному юзеру
                response = self.authorized_client.get(addr)
                self.assertEqual(response.status_code, resp_login,
                                 addr + ' недоступна авторизованному'
                                 ' пользователю')

                # Правильность шаблона
                if addr != '/unexisting_page':
                    self.assertTemplateUsed(response, templ, 'для ' + addr
                                            + ' недоступен шаблон ' + templ)

    def test_post_detail_url_redirect_anonymous(self):
        """Страница /posts/<post_id>/edit/ перенаправляет авторизованного,
        но не имеющего отношения к авторству поста, пользователя.
        """
        # авторизуем отличного, от автора тестового поста, пользователя
        self.authorized_client.force_login(self.user)
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)
