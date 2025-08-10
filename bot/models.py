from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


class LoginCode(models.Model):
    chat_id = models.BigIntegerField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=1)

    def __str__(self):
        return f"{self.chat_id} - {self.code}"

    class Meta:
        verbose_name = _("Kirish kodi ")
        verbose_name_plural = _("Kirish kodlari")