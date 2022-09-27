from django.test import TestCase

from posts.models import Group, Post, User, Comment


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        func_expect_value = [
            (post._meta.get_field('text').verbose_name, 'Текст поста'),
            (post._meta.get_field('pub_date').verbose_name,
                'Дата публикации'),
            (post._meta.get_field('author').verbose_name, 'Автор'),
            (post._meta.get_field('group').verbose_name, 'Группа'),
            (post._meta.get_field('image').verbose_name, 'Картинка'),
            (group._meta.get_field('title').verbose_name, 'Имя группы'),
            (group._meta.get_field('description').verbose_name, 'Описание'),
            (comment._meta.get_field('post').verbose_name, 'Пост к которому оставлен комментарий'),
            (comment._meta.get_field('author').verbose_name, 'Автор комментария'),
            (comment._meta.get_field('text').verbose_name, 'Комментарий'),
            (comment._meta.get_field('created').verbose_name, 'Дата публикации'),
            (post._meta.get_field('text').help_text, 'Введите текст поста'),
            (post._meta.get_field('group').help_text,
                'Группа, к которой будет относиться пост'),
            (comment._meta.get_field('text').help_text, 'Напишите комментарий'),
            (post._meta.get_field('image').help_text, 'Загрузите картинку')
        ]
        for func_result, expected_value in func_expect_value:
            with self.subTest(
                func_result=func_result,
                expected_value=expected_value
            ):
                self.assertEqual(func_result, expected_value)

    def test_text_slug_max_length_not_exceed(self):
        """
        Длинный title обрезается и не превышает max_length поля title в модели
        Group."""
        group = PostModelTest.group
        max_length_slug = group._meta.get_field('title').max_length
        length_title = len(group.title)
        self.assertEqual(max_length_slug, length_title)
