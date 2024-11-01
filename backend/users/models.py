from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 기본 필드 외 추가 필드
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # 프로필 이미지
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # 이메일 인증 관련
    email_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'custom_user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return self.email