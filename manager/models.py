from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    about = models.TextField(max_length=70, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Foydalanuvchi "
        verbose_name_plural = "Foydalanuvchilar"


class Article(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Maqola "
        verbose_name_plural = "Maqolalar"


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='article_images/')

    def __str__(self):
        return f"Rasm: {self.article.title}"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"

    class Meta:
        verbose_name = "Izoh "
        verbose_name_plural = "Izohlar"
        ordering = ['-created_at']


class Notification(models.Model):

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=50)
    message = models.CharField(max_length=255)
    link = models.URLField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} uchun {self.message}"

    class Meta:
        verbose_name = "Bildirishnoma "
        verbose_name_plural = "Bildirishnomalar"
        ordering = ['-created_at']