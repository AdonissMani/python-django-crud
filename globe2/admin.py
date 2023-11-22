from django.contrib import admin
from .models import Country
from .models import State
from .models import City
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


admin.site.register(CustomUser)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)