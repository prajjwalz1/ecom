# accounts/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# User = get_user_model()


# class TokenObtainPairSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         username = attrs.get('username')
#         password = attrs.get('password')

#         if username and password:
#             try:
#                 user = User.objects.get(username=username)
#             except User.DoesNotExist:
#                 raise serializers.ValidationError('Invalid credentials')

#             if not user.check_password(password):
#                 raise serializers.ValidationError('Invalid credentials')

#             refresh = RefreshToken.for_user(user)
#             return {'access': str(refresh.access_token), 'refresh': str(refresh)}

#         raise serializers.ValidationError('Must include username and password')
