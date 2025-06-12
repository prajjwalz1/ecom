# accounts/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

from user.models import CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "is_staff",
            "created_by",
        )

    def create(self, validated_data):
        # 1) Extract the fields that create_user expects positionally/explicitly:
        password = validated_data.pop("password", None)
        username = validated_data.pop("username")
        email = validated_data.pop("email")

        # 2) Pull out created_by if passed (from serializer.save(created_by=...))
        created_by = validated_data.pop("created_by", None)

        # 3) Call your manager method without duplicates
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            created_by=created_by,
            **validated_data  # any other extra fields
        )

        return user


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data.get("phone_number", ""),
        )
        return user


class TokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")

            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials")

            refresh = RefreshToken.for_user(user)
            return {"access": str(refresh.access_token), "refresh": str(refresh)}

        raise serializers.ValidationError("Must include username and password")
