from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
# Create your models here


class UserManager(BaseUserManager):
    # REQUIRED_FIELDS,default is
    def create_user(self, email, password=None, username=None, is_active=True, is_customer=False, is_staff=False, is_admin=False):
        if not email:  # email and password,eg username if req
            raise ValueError("Users must have email address")
        if not password:
            raise ValueError("Users must have password")
        user_obj = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user_obj.set_password(password)  # change user password
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.customer = is_customer
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, username=None, password=None):
        user = self.create_user(
            email,
            username=username,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, username=None, password=None):
        user = self.create_user(
            email,
            username=username,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user

    def create_customeruser(self, email, username=None, password=None):
        user = self.create_user(
            email,
            username=username,
            password=password,
            is_customer=True
        )
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    active = models.BooleanField(default=True)  # can login
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    customer = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'  # username

    REQUIRED_FIELDS = []  # ['full_name','email'..] #python manage.py createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_full_name(self):
        if self.username:
            return self.username
        return self.email

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    @property
    def is_customer(self):
        return self.customer

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)
