from django.test import TestCase

from posts.models import Comment, Group, Follow, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower_user = User.objects.create_user(
            username='Подписчик'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='А' * 200,
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            text='Текст поста',
            author=cls.user,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.follower_user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        model_str = [
            (PostModelTest.comment, PostModelTest.comment.text),
            (PostModelTest.post, PostModelTest.post.text[:15]),
            (PostModelTest.group, PostModelTest.group.title)
        ]
        for model, string in model_str:
            with self.subTest(model=model, string=string):
                self.assertEqual(str(model), string)

    def test_verbose_name_help_text(self):
        """verbose_name и help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        follow = PostModelTest.follow
        func_expect_value_verb_name = [
            (post, [
                ('text', 'Текст поста'),
                ('pub_date', 'Дата публикации'),
                ('author', 'Автор'),
                ('group', 'Группа'),
                ('image', 'Картинка')
            ]),
            (group, [
                ('title', 'Имя группы'),
                ('description', 'Описание')
            ]),
            (comment, [
                ('text', 'Комментарий'),
                ('created', 'Дата публикации'),
                ('author', 'Автор комментария'),
                ('post', 'Пост')
            ]),
            (follow, [
                ('author', 'Автор'),
                ('user', 'Подписчик')
            ])
        ]
        for model, part_model in func_expect_value_verb_name:
            for key, expected_value in part_model:
                with self.subTest(
                    key=key,
                    expected_value=expected_value
                ):
                    func_result = model._meta.get_field(key).verbose_name
                    self.assertEqual(func_result, expected_value)
        func_expect_value_help_text = [
            (post, [
                ('text', 'Введите текст поста'),
                ('group', 'Группа, к которой будет относиться пост'),
                ('image', 'Загрузите картинку')
            ]),
            (comment, [
                ('text', 'Напишите комментарий'),
                ('post', 'Пост к которому оставлен комментарий')
            ])
        ]
        for model, part_model in func_expect_value_help_text:
            for key, expected_value in part_model:
                with self.subTest(
                    key=key,
                    expected_value=expected_value
                ):
                    func_result = model._meta.get_field(key).help_text
                    self.assertEqual(func_result, expected_value)

    def test_text_slug_max_length_not_exceed(self):
        """
        Длинный title обрезается и не превышает max_length поля title в модели
        Group."""
        group = PostModelTest.group
        max_length_slug = group._meta.get_field('title').max_length
        length_title = len(group.title)
        self.assertEqual(max_length_slug, length_title)
