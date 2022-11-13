import tempfile
import shutil

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, User
from posts.forms import PostForm, CommentForm
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

        cls.author = User.objects.create_user(username='author')

        cls.post = Post.objects.create(
            group=PostCreateFormTests.group,
            text="Тестовый текст",
            author=User.objects.get(username='author'),
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = User.objects.create_user(username='WithoutName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
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
        self.form_data = {
            'group': self.group.pk,
            'text': 'Пост с картинкой',
            'image': self.uploaded,
        }

    def test_form_create(self):
        """Проверка создания нового поста"""
        post_count = Post.objects.count()
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=self.form_data,
                                               follow=True)
        new_post = Post.objects.get(
            group=self.form_data['group'],
            text=self.form_data['text'],
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user]
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(new_post.text, self.form_data['text'])
        self.assertEqual(new_post.group.title, self.group.title)
        self.assertIsNotNone(new_post.image)

    def test_form_edit(self):
        """Проверка редактирования поста"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        form_data = {
            'group': self.group.id,
            'text': 'Обновленный текст',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data, follow=True)

        self.assertTrue(Post.objects.filter(
            text='Обновленный текст',
            group=PostCreateFormTests.group).exists())

    def test_comment_form(self):
        """Проверяем форму комментариев"""
        form_data = {'text': 'тестовый комментарий'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
