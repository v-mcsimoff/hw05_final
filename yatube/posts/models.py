from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='название группы')
    description = models.TextField(verbose_name='описание')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Url адрес'
    )

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Обязательное поле'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        related_name='posts',
        help_text='Выберите группу или оставьте пустым',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        ordering = ('-created',)

    def __str__(self):
        return self.text


class Comment(CreatedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments", verbose_name='Пост',
                             help_text='Комментируемый пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name='Автор комментария',
                               help_text='Автор отображается на сайте')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Обязательное поле')

    class Meta:
        verbose_name_plural = 'Комментарии к постам'
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
