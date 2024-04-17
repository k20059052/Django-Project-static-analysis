from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class CustomUserManager(UserManager):
    """
    UserManager which allows users of different roles to be added as well as a superuser
    which bypass the need to have default fields such as username
    """

    def create_user(
        self,
        email,
        password=None,
        first_name=None,
        last_name=None,
        **extra_fields
    ):
        if not email:
            raise ValueError('Enter an email address')
        if not first_name:
            raise ValueError('Enter a first name')
        if not last_name:
            raise ValueError('Enter a last name')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.role = 'ST'
        user.save(using=self._db)
        return user

    def create_specialist(
        self,
        email,
        password=None,
        first_name=None,
        last_name=None,
        **extra_fields
    ):
        if not email:
            raise ValueError('Enter an email address')
        if not first_name:
            raise ValueError('Enter a first name')
        if not last_name:
            raise ValueError('Enter a last name')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.role = 'SP'
        user.save(using=self._db)
        return user

    def create_director(
        self,
        email,
        password=None,
        first_name=None,
        last_name=None,
        **extra_fields
    ):
        if not email:
            raise ValueError('Enter an email address')
        if not first_name:
            raise ValueError('Enter a first name')
        if not last_name:
            raise ValueError('Enter a last name')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.role = 'DI'
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name, last_name):
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_superuser = True
        user.is_staff = True
        user.role = 'DI'
        user.save(using=self._db)
        return user

    def create_custom_user(self, email, password, first_name, last_name, role):
        user = self.create_user(
            email.lower(),
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.role = role
        user.save(using=self._db)
        return user


# seed done
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False)
    # first_name = models.CharField(max_length=50)
    first_name = models.CharField(
        blank=False,
        unique=False,
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z\s]{1,}$',
                message='First Name must consist of 1-50 letters',
            )
        ],
    )

    last_name = models.CharField(
        blank=False,
        unique=False,
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z\s]{1,}$',
                message='Last Name must consist of 1-50 letters',
            )
        ],
    )

    class Role(models.TextChoices):
        STUDENT = 'ST'
        SPECIALIST = 'SP'
        DIRECTOR = 'DI'

    role = models.CharField(
        max_length=2, choices=Role.choices, default=Role.STUDENT
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()
    class Meta:
        ordering = ['id']


    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super(User, self).save(*args, **kwargs)
