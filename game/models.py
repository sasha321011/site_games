from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Game.Status.PUBLISHED)


# Create your models here.
class Game(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'

    title = models.CharField(max_length=50, verbose_name='Заголовок')
    price = models.PositiveIntegerField(verbose_name='Цена')
    content = models.CharField(blank=True, max_length=500)
    slug = models.SlugField(blank=True)
    image = models.FileField(blank=True, upload_to='photos/%Y/%m/%d/', default=None, null=True, verbose_name='Фото')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    saled_count = models.PositiveIntegerField(null=True, default=0)
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                       default=Status.DRAFT, verbose_name='Статус')
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name='Теги')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True
                               )

    objects = models.Manager()
    published = PublishedManager()

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            unique_slug = self.slug
            num = 1
            while Game.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    def __str__(self):
        return self.tag


class Comments(models.Model):
    text_comment = models.TextField(max_length=2500, verbose_name="Комментарий")
    post = models.ForeignKey(Game,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f"Комментарий от {self.author} на {self.post.title}"


class UserVote(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='votes')
    vote = models.SmallIntegerField(choices=VOTE_CHOICES, null=True)

    class Meta:
        unique_together = ('user', 'game')  # Ограничение: один пользователь - один голос за игру


class Basket(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(Game,on_delete=models.CASCADE,related_name='added_game')
    quantity = models.PositiveIntegerField()
    all_price = models.PositiveIntegerField()