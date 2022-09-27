from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import Post, Group, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=User.objects.create_user(username='test_iliya')
        )
        cls.group = Group.objects.create(
            slug='test_slug',
            title='Тестовая группа',
            description='Тестовое описание'
        )
        cls.pattern_matching = [
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.post.author}/', 'posts/profile.html'),
            (f'/posts/{cls.post.pk}/', 'posts/post_detail.html'),
            ('/create/', 'posts/create_post.html'),
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)

    def test_correct_urls_authorized(self):
        """URL-адреса доступны авторизованному
        пользователю и используют правильные шаблоны
        """
        for url, template in self.pattern_matching:
            with self.subTest(
                url=url,
                template=template
            ):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_page(self):
        """Проверка доступности страниц автора"""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Тест несуществующей страницы"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страницы перенаправят анонимного
        пользователя.
        """
        redirect_page = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.pk}/edit/': f"/posts/{self.post.pk}/",
        }
        for address, template in redirect_page.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, template)
