import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.core.cache import cache
from django.urls import reverse
from django import forms

from posts.models import Comment, Group, Follow, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )  # изображение


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower_user = User.objects.create(username='test_follower')
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            slug='test_slug',
            title='test_title',
            description='test_description'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='text_post',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            text='Коммент',
            author=cls.author,
            post=cls.post
        )
        cls.index_page = reverse('posts:index')
        cls.group_list_page = reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}
        )
        cls.profile_page = reverse(
            'posts:profile', kwargs={'username': 'test_user'}
        )
        cls.post_detail_page = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.pk}
        )
        cls.post_create_page = reverse('posts:post_create')
        cls.post_edit_page = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.pk}
        )
        cls.urls_list = [
            (cls.index_page, 'posts/index.html'),
            (cls.group_list_page, 'posts/group_list.html'),
            (cls.profile_page, 'posts/profile.html'),
            (cls.post_detail_page, 'posts/post_detail.html'),
            (cls.post_create_page, 'posts/create_post.html'),
            (cls.post_edit_page, 'posts/create_post.html')
        ]
        cls.pages_with_paginator = [
            cls.index_page,
            cls.group_list_page,
            cls.profile_page
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTest.author)
        self.follower_client = Client()
        self.follower_client.force_login(PostViewsTest.follower_user)

    def asserts(self, first_object):
        self.assertEqual(first_object.author, PostViewsTest.post.author)
        self.assertEqual(first_object.text, PostViewsTest.post.text)
        self.assertEqual(first_object.group, PostViewsTest.post.group)
        self.assertEqual(
            first_object.group.slug, PostViewsTest.post.group.slug
        )
        self.assertEqual(
            first_object.group.description,
            PostViewsTest.post.group.description
        )
        self.assertEqual(first_object.image, PostViewsTest.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in PostViewsTest.urls_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_cache(self):
        """Проверка кеша страницы index"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.post.delete()
        response_after_delete = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response_after_delete.content, response.content)
        cache.clear()
        response_after_clear_cache = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response_after_clear_cache.content, response.content
        )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostViewsTest.index_page)
        first_object = response.context.get('post')
        self.asserts(first_object)
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostViewsTest.group_list_page)
        first_object = response.context.get('post')
        self.asserts(first_object)
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostViewsTest.profile_page)
        first_object = response.context.get('post')
        self.asserts(first_object)
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostViewsTest.post_detail_page)
        first_object = response.context.get('post')
        self.asserts(first_object)
        # self.assertEqual(
        #     response.context['post'].comments, PostViewsTest.post.comments
        # )
        self.assertEqual(response.context['title'], f'Пост {self.post.text}')
        form_fields = {
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostViewsTest.post_create_page)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostViewsTest.post_edit_page)
        first_object = response.context.get('post')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context['is_edit'])
        self.asserts(first_object)

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может подписаться на автора
        и отписаться."""
        self.follower_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostViewsTest.author.username})
        )
        follow_count = Follow.objects.all().count()
        self.assertEqual(follow_count, 1)
        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostViewsTest.author.username})
        )
        unfollow_count = Follow.objects.all().count()
        self.assertEqual(unfollow_count, 0)

    def test_new_post_appears_in_the_subscribers(self):
        """Новый пост появляется у подписчиков автора поста
        и отсутвует у тех кто не подписан на автора."""
        self.new_post = Post.objects.create(
            group=PostViewsTest.group,
            author=PostViewsTest.author,
            text='Написал новый пост'
        )
        Follow.objects.create(
            user=PostViewsTest.follower_user,
            author=PostViewsTest.author
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj'].object_list), 2
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotContains(
            response, self.new_post.text
        )

    def test_page_paginator(self):
        """Проверка Пагинатора"""
        self.posts = [
            Post(
                text=f'text {i}', author=self.author, group=self.group
            ) for i in range(12)
        ]
        Post.objects.bulk_create(self.posts)
        postfixurl_posts = [(1, 10), (2, 3)]
        for postfixurl, posts in postfixurl_posts:
            for page in PostViewsTest.pages_with_paginator:
                with self.subTest(page=page):
                    response = self.authorized_client.get(
                        page, {'page': postfixurl}
                    )
                    self.assertEqual(len(response.context['page_obj']), posts)
