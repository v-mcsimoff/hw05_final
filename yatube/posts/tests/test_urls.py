from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post',
        )

    def setUp(self):
        # Creating an unauthorized client
        self.guest_client = Client()
        # Create a second client
        self.authorized_client = Client()
        # Authorizing the user
        self.authorized_client.force_login(self.user)

    def test_pages_at_desired_location_for_all(self):
        """Pages are available to everyone."""
        url_names = (
            '/',
            '/group/test_slug/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_at_desired_location_for_authorized(self):
        """The /create/ pages are available to an authorized
        user."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_at_desired_location_author(self):
        """The posts/<post_id>/edit/ page is accessible to the author."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url(self):
        """The unexisting_page is not available to any user."""
        response = self.guest_client.get('/<unexisting_page>/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """The URL uses an appropriate template."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
