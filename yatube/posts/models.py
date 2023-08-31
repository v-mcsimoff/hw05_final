from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='group name')
    description = models.TextField(verbose_name='description')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Url adress'
    )

    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Post text',
        help_text='Required field'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='author'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Group',
        related_name='posts',
        help_text='Choose a group or leave blank',
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ('-created',)

    def __str__(self):
        return self.text


class Comment(CreatedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments", verbose_name='Post',
                             help_text='Commented post')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name='Comment author',
                               help_text='The author is displayed on the website')
    text = models.TextField(verbose_name='Comment text',
                            help_text='Required field')

    class Meta:
        verbose_name_plural = 'Posts comments'
        ordering = ('-created',)

    def __str__(self):
        return self.text


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    body = models.TextField()
    is_answered = models.BooleanField(default=False)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')
