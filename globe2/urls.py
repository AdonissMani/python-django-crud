# YourAppName/urls.py
from django.urls import path
from .views import *


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    # path('logout/', UserLogoutView.as_view(), name='logout'),
    path("users/", UserList.as_view(), name="user-view"),
    path("countries/", CountryList.as_view(), name="country-list"),
    path("countries/<int:pk>/", CountryDetailView.as_view(), name="country_detail"),
    path(
        "countries/<int:country_id>/states/",
        StateList.as_view(
            {"get": "list", "post": "create", "put": "update", "delete": "destroy"}
        ),
        name="state-list",
    ),
    path(
        "countries/<int:country_id>/states/<int:state_id>/cities/",
        CityList.as_view(
            {"get": "list", "post": "create", "put": "update", "delete": "destroy"}
        ),
        name="city-list",
    ),
    path("nested/", NestedCRUD.as_view(), name="nested-view"),
    path("nested/<int:pk>/", NestedUpdateDelete.as_view(), name="nested-update"),
]
