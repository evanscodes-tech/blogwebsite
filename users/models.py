from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    # Role choices
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        AUTHOR = 'author', _('Author')
        READER = 'reader', _('Reader')
    
    # Custom fields we already have
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True)
    
    # NEW: Add role field
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.READER
    )
    
    # NEW: Email verification fields
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.username
    
    # Helper methods
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_staff
    
    def is_author(self):
        return self.role == self.Role.AUTHOR or self.is_admin()
    
    def is_reader(self):
        return self.role == self.Role.READER