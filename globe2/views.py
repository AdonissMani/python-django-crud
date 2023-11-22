from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer,
    LoginSerializer,
    CountrySerializer,
    StateSerializer,
    CitySerializer,
)
from .models import CustomUser, Country, State, City

# Paginator class
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100

# User registration view
class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer_class):
        user = serializer_class.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token) # type: ignore
        response_data = {
            "detail": "User registered successfully.",
            "access_token": access_token,
        }

# User login view
class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"] # type: ignore
            password = serializer.validated_data["password"] # type: ignore
            user = authenticate(request, email=email, password=password)

            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token) # type: ignore

                response_data = {
                    "status": status.HTTP_200_OK,
                    "message": "success",
                    "data": {"Token": access_token},
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Unable to log in with provided credentials."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

# Nested view for list and creating countries
class NestedCRUD(generics.ListCreateAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Country.objects.filter(my_user=self.request.user)

    def get_serializer_context(self):
        return {"view": self}

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()

# Nested view for country-state-city update
class NestedUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CountrySerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Country.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

# Listing all Country for a user
class CountryList(generics.ListCreateAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Country.objects.filter(my_user=user)

# Listing detailed view of a country for the user
class CountryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        country_id = self.kwargs["pk"]
        states = State.objects.filter(country_id=country_id)
        return Country.objects.filter(id=country_id)

# Listing all states
class StateList(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    def get_queryset(self):
        country_id = self.kwargs["country_id"]
        return State.objects.filter(country_id=country_id)

    def get_my_country_name(self):
        country_id = self.kwargs["country_id"]
        country = Country.objects.get(id=country_id)
        return {"my_country_name": country.countryName}

    def get_my_country_my_user_name(self):
        country_id = self.kwargs["country_id"]
        country = Country.objects.get(id=country_id)
        return {"my_user_name": country.my_user}

# Listing all City
class CityList(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    def get_queryset(self):
        state_id = self.kwargs["state_id"]
        return City.objects.filter(state_id=state_id)

    def get_my_state_name(self):
        state_id = self.kwargs["state_id"]
        state = State.objects.get(id=state_id)
        return {"my_state_name": state.stateName}

# Listing all Users
class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination


