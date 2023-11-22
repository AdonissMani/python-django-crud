
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.forms import ValidationError
import jwt
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken

class CustomUserManager(BaseUserManager):
    # creating user
    def create_user(self, email, password, **extra_fields):
        print("i am CustomUserManager")
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    # creating super user
    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


# custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    print("i am CustomUser")
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email




@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def generate_jwt_token(sender, instance=None, **kwargs):
    if instance and instance.pk is None:
        # This is a new user instance being created
        refresh = RefreshToken.for_user(instance)
        instance.refresh_token = str(refresh)
        instance.access_token = str(refresh.access_token) # type: ignore

# country model
class Country(models.Model):
    countryName = models.CharField(max_length=50)
    countryCode = models.CharField(max_length=10, unique=True)
    phoneCode = models.IntegerField(unique=True)
    my_user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.countryName


# state model
class State(models.Model):
    stateName = models.CharField(max_length=50, unique=True)
    stateCode = models.CharField(max_length=50)
    GST_code = models.CharField(max_length=50, unique=True)

    country = models.ForeignKey("Country", on_delete=models.CASCADE)

    def get_my_country_name(self):
        return self.country.countryName if self.country else None

    def get_my_country_my_user_name(self):
        return self.country.my_user if self.country else None

    def __str__(self):
        return self.stateName


# city model
class City(models.Model):
    cityName = models.CharField(max_length=50, unique=True)
    cityCode = models.CharField(max_length=50, unique=True)
    population = models.IntegerField()
    avg_age = models.FloatField()
    num_of_male = models.IntegerField()
    num_of_female = models.IntegerField()
    # state as foreign key
    state = models.ForeignKey("State", on_delete=models.CASCADE)

    def get_my_state_name(self):
        return self.state.stateName if self.state else None

    # validating population
    def populationControl(self):
        if self.population < self.num_of_male + self.num_of_female:
            raise ValidationError(
                "Population must be greater than sum of adult males & females."
            )

    def __str__(self):
        return self.cityName
