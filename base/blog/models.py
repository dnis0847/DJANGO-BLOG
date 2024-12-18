from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import markdown

# Create your models here.
from django.db import models


class Category(models.Model):
    # Название категории, уникальное
    name = models.CharField(max_length=100, unique=True)
    # Slug для URL, уникальный
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        # Сортировка по названию
        ordering = ['name']
        # Индекс по полю name для ускорения поиска
        indexes = [
            models.Index(fields=['name']),
        ]

    # Строковое представление объекта
    def __str__(self):
        return self.name

    # URL для категории
    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"


class Tag(models.Model):
    # Название тега, уникальное
    name = models.CharField(max_length=100, unique=True)
    # Slug для URL, уникальный
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        # Сортировка по названию
        ordering = ['name']
        # Индекс по полю name для ускорения поиска
        indexes = [
            models.Index(fields=['name']),
        ]

    # Строковое представление объекта
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/tag/{self.slug}/"


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    class ContentType(models.TextChoices):
        PLAIN = 'PL', 'Plain Text'
        MARKDOWN = 'MD', 'Markdown'

    # Заголовок поста
    title = models.CharField(max_length=250)
    # Slug для URL, уникальный для даты публикации
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # Изображение для поста
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    # Содержимое поста
    content = models.TextField()
    # Тип контента (обычный текст или Markdown)
    content_type = models.CharField(
        max_length=2, choices=ContentType.choices, default=ContentType.PLAIN)
    # Автор поста, связь с моделью User
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    # Дата создания поста
    created = models.DateTimeField(auto_now_add=True)
    # Дата последнего обновления поста
    updated = models.DateTimeField(auto_now=True)
    # Категория поста, связь с моделью Category
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='posts')
    # Дата публикации поста
    publish = models.DateTimeField(default=timezone.now)
    # Статус поста (черновик или опубликован)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT)
    # Теги поста, связь многие-ко-многим с моделью Tag
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    # Новое поле для хранения количества просмотров
    views = models.PositiveIntegerField(default=0)

    class Meta:
        # Сортировка по дате публикации (по убыванию)
        ordering = ['-publish']
        # Индекс по полю publish для ускорения поиска
        indexes = [
            models.Index(fields=['-publish']),
        ]

    # Строковое представление объекта
    def __str__(self):
        return self.title

    # Получение количества комментариев к посту
    def get_comments_count(self):
        return self.comments.count()

    # URL для поста
    def get_absolute_url(self):
        return f"/blog/post/{self.slug}/"

    # Метод для форматирования контента
    def get_formatted_content(self):
        if self.content_type == self.ContentType.MARKDOWN:
            return markdown.markdown(self.content, extensions=['fenced_code', 'codehilite'])
        return self.content

    # Метод для получения похожих постов
    def get_similar_posts(self):
        return Post.objects.filter(
            category=self.category).exclude(
                pk=self.pk).order_by('-views')


class Comment(models.Model):
    # Пост, к которому относится комментарий, связь с моделью Post
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    # Имя автора комментария
    name = models.CharField(max_length=80)
    # Email автора комментария
    email = models.EmailField()
    # Содержимое комментария
    body = models.TextField()
    # Дата создания комментария
    created = models.DateTimeField(auto_now_add=True)
    # Дата последнего обновления комментария
    updated = models.DateTimeField(auto_now=True)
    # Статус активности комментария
    active = models.BooleanField(default=True)

    class Meta:
        # Сортировка по дате создания
        ordering = ['created']
        # Индекс по полю created для ускорения поиска
        indexes = [
            models.Index(fields=['created']),
        ]

    # Строковое представление объекта
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

    # URL для комментария
    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#comment-{self.id}"


class UserProfile(models.Model):
    USER = 'USER'
    AUTHOR = 'AUTHOR'
    EDITOR = 'EDITOR'
    ADMIN = 'ADMIN'

    ROLE_CHOICES = [
        (USER, 'User'),
        (AUTHOR, 'Author'),
        (EDITOR, 'Editor'),
        (ADMIN, 'Admin'),
    ]

    # Связь один-к-одному с моделью User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Описание пользователя, необязательное поле
    description = models.TextField(blank=True)
    # Аватар пользователя, необязательное поле
    avatar = models.ImageField(upload_to='images/avatars/', blank=True)
    # Роль пользователя
    role = models.CharField(max_length=6, choices=ROLE_CHOICES, default=USER)

    # Строковое представление объекта
    def __str__(self):
        return self.user.username

    # URL для профиля пользователя
    def get_absolute_url(self):
        return f"/blog/user/{self.user.username}/"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class Contacts(models.Model):
    address = models.CharField(max_length=250, verbose_name='Адрес')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    work_time = models.CharField(max_length=100, verbose_name='Время работы')

    def __str__(self):
        return self.adress

    class Meta:
        verbose_name = 'Contacts'
        verbose_name_plural = 'Contacts'


class SocialNetworks(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Social Networks'
        verbose_name_plural = 'Social Networks'


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

