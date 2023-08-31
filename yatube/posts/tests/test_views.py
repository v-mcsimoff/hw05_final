import tempfile

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, User, Comment, Follow
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
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
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test new post',
            group=cls.group,
            image=uploaded
        )
        cls.group2 = Group.objects.create(
            title='Test group2',
            slug='test_slug2',
            description='Test description2',
        )

    def setUp(self):
        # Creating an unauthorized client
        self.guest_client = Client()
        # Create a second client
        self.authorized_client = Client()
        # Authorizing the user
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """The URL uses the appropriate template."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ),
            'posts/profile.html': reverse('posts:profile', args={self.user}),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """The index template is generated with the correct context.
        It displays the created post"""
        response = self.authorized_client.get(reverse('posts:index'))
        object = response.context["page_obj"][0]
        post_text = object.text
        post_author = object.author.username
        post_group = object.group
        post_image = Post.objects.first().image
        self.assertEqual(post_text, 'Test new post')
        self.assertEqual(post_author, 'author')
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_image, 'posts/small.gif')

    def test_group_list_show_correct_context(self):
        """The group template is generated with the correct context."""
        response = self.authorized_client.get(reverse
                                              ('posts:group_list',
                                               kwargs={'slug': 'test_slug'}))
        object = response.context['group']
        group_title = object.title
        group_slug = object.slug
        self.assertEqual(group_title, 'Test group')
        self.assertEqual(group_slug, 'test_slug')

    def test_post_on_group_list(self):
        """The post is displayed on the group page"""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug]))
        object = response.context['posts'][0]
        post_text = object.text
        post_group = object.group.title
        post_image = Post.objects.first().image
        self.assertEqual(post_text, 'Test new post')
        self.assertEqual(post_group, 'Test group')
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_another_group(self):
        """The post hasn't ended up in a different group"""
        Post.objects.create(
            author=self.user, text='Test post 2', group=self.group2
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug2'}))
        object = response.context['page_obj'][0]
        self.assertNotEqual(object, self.post)

    def test_profile_correct_context(self):
        """The profile template is generated with the correct context.
        It displays the created post"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'author'}))
        post = response.context['page_obj'][0]
        self.post = post.text
        post_image = Post.objects.first().image
        self.assertEqual(response.context['author'].username, 'author')
        self.assertEqual(self.post, 'Test new post')
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_detail_show_correct_context(self):
        """The post_detail template is generated with the correct context."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')
        for post in Post.objects.select_related('group'):
            self.assertEqual(response.context.get('post'), post)

    def test_post_create_show_correct_context(self):
        """The post_create template is generated with the correct context."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """The post_edit template is generated with the correct context."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'image': forms.ImageField,
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='author'),
            text='Test post')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='author2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment_authorized(self):
        """Registered user can add comments."""
        item = Post.objects.first()
        form_data = {
            'text': 'Test comment',
            'author': self.user,
            'post': self.post,
        }
        self.authorized_client.post(reverse('posts:add_comment',
                                            args=[item.id]),
                                    data=form_data, follow=True)
        last_comment = (
            Comment.objects.filter(author__username='author2').last()
        )
        self.assertEqual(form_data['text'], last_comment.text)
        self.assertEqual(item.id, last_comment.post.id)
        self.assertEqual(str(last_comment.author), 'author2')


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='author'),
            text='Test post')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='author2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_on_index_page(self):
        """Cache on the main page"""
        response = self.authorized_client.get(reverse('posts:index'))
        before_clearing_cache = response.content
        Post.objects.create(
            text='Text after the cache',
            author=User.objects.get(username='author'))
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        after_clearing_cache = response.content
        self.assertNotEqual(before_clearing_cache,
                            after_clearing_cache)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower')
        self.user_following = User.objects.create_user(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Test post for the feed'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        """The subscription function check."""
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """The un-subscription function check."""
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username':
                                              self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        """The entry is displayed in the feed."""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get('/follow/')
        post = response.context["page_obj"][0]
        self.assertEqual(post.text, 'Test post for the feed')
        self.assertTrue(
            Follow.objects.filter(user=self.user_follower,
                                  author=self.user_following).exists()
        )
        response = self.client_auth_following.get('/follow/')
        self.assertNotContains(response,
                               'Test post for the feed')


class PaginatorViewsTest(TestCase):
    TOTAL_POSTS = 13
    FIRST_PAGE_POSTS = 10
    SECOND_PAGE_POSTS = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description',
        )
        cls.posts = []
        for i in range(cls.TOTAL_POSTS):
            cls.posts.append(Post(
                text=f'Test new post {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='WithoutName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        list_urls = {
            reverse('posts:index'): '/',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): 'group',
            reverse('posts:profile', kwargs={'username': 'author'}): 'profile',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list),
                self.FIRST_PAGE_POSTS
            )

    def test_second_page_contains_three_posts(self):
        list_urls = {
            reverse('posts:index') + '?page=2': '/',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
            + '?page=2': 'group',
            reverse('posts:profile', kwargs={'username': 'author'})
            + '?page=2': 'profile',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list),
                self.SECOND_PAGE_POSTS
            )
