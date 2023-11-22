# YourAppName/serializers.py
from django.shortcuts import redirect
from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from typing import List, OrderedDict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# user serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email","password"]
        extra_kwargs = {"password": {"write_only": True}}

    print("i am User serializer")

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)  # type: ignore
        return user


# login serializer
class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                data["user"] = user
                existing_token = Token.objects.filter(user=user).first()
                if existing_token:
                    # Return the existing token
                    data["token"] = existing_token
                else:
                    # Create a new token
                    token = Token.objects.create(user=user)
                    data["token"] = token
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        return data


# city serializer
class CitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    my_state_name = serializers.CharField(source="get_my_state_name", read_only=True)

    class Meta:
        model = City
        fields = [
            "id",
            "cityName",
            "cityCode",
            "population",
            "avg_age",
            "num_of_male",
            "num_of_female",
            "my_state_name",
        ]
        read_only_fields = ["State"]


# State serializer
class StateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    my_country_name = serializers.CharField(
        source="get_my_country_name", read_only=True
    )
    my_country_my_user_name = serializers.CharField(
        source="get_my_country_my_user_name", read_only=True
    )
    city_set = CitySerializer(many=True)

    class Meta:
        model = State
        fields = [
            "id",
            "stateName",
            "stateCode",
            "GST_code",
            "my_country_name",
            "my_country_my_user_name",
            "city_set",
        ]
        read_only_fields = ["Country"]


# country serializer
class CountrySerializer(serializers.ModelSerializer):
    state_set = StateSerializer(many=True)
    # my_user = UserSerializer(many=False,allow_null=False)

    class Meta:
        model = Country
        fields = ["id", "countryName", "countryCode", "phoneCode", "state_set"]
        # read_only_fields = ['my_user']

    def validate(self, data: OrderedDict):

        return data

    # create method overrided for nesting
    def create(self, validated_data):

        cities: List[City] = []
        states: List[State] = []

        states_data = validated_data.pop("state_set", [])
        # creating country instance
        country = Country.objects.create(
            my_user=self.context["view"].request.user, **validated_data
        )

        for state_data in states_data:
            print("i am 1")
            # extracting city data
            cities_data = state_data.pop("city_set", [])
            state = State(country=country, **state_data)
            states.append(state)

            for city_data in cities_data:
                cities.append(City(state_id=state_data["id"], **city_data))

        # Bulk create state
        State.objects.bulk_create(states)

        # Bulk create city
        City.objects.bulk_create(cities)

        # State.objects.filter(my_country=country).delete()
        # City.objects.filter(my_state__my_country=country).delete()

        return country

    # nested update method overriding
    def update(self, instance, validated_data):

        # Extract state data from validated_data
        states_data = validated_data.pop("state_set", [])

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            instance.countryName = validated_data.get(
                "countryName", instance.countryName
            )
            instance.countryCode = validated_data.get(
                "countryCode", instance.countryCode
            )
            instance.phoneCode = validated_data.get("phoneCode", instance.phoneCode)
            instance.save()
            # Delete existing states and cities
            instance.state_set.all().delete()

            # Create new states and cities
            new_states = []
            for state_data in states_data:
                cities_data = state_data.pop("city_set", [])
                state_instance = State.objects.create(country=instance, **state_data)
                new_states.append(state_instance)

                # Create new cities for the current state
                City.objects.bulk_create(
                    [
                        City(state=state_instance, **city_data)
                        for city_data in cities_data
                    ]
                )

        return instance
