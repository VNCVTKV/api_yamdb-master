from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()
# Create your models here.


class Category(models.Model):
    name = models.CharField(
        'название',
        max_length=256,
        default=None
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        'название',
        max_length=256,
        default=None
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=256
    )
    year = models.IntegerField(
        'год',
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name
    

class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.IntegerField()

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_relationships'
            ),
        ]

    def clean_score(self, value):
        if not 1 <= value <= 10:
            raise ValidationError({'score': 'score must be between 1 and 10.'})
    
    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        blank=False
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('id',)