from django.contrib.auth import authenticate
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny

# User = get_user_model()
# Create your views here.
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class CustomTokenObtainView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        # Serialize incoming data
        print(request.data)
        serializer = CustomAuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Authenticate user manually
            user = authenticate(request, email=email, password=password)
            
            if user.is_authenticated:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                
                # Return tokens in custom format
                return Response({
                    'success': True,
                    'message': 'Authentication successful',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'data':[]
                
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'error',
                'message': 'Invalid credentials',
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # If serializer is invalid, return error
        return Response({
            'status': 'error',
            'message': 'Invalid data',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework_simplejwt.serializers import TokenRefreshSerializer

class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]  # Allows access to all users

    def post(self, request, *args, **kwargs):
        # Use TokenRefreshSerializer to handle refresh token
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            # Customize the response format with the new access token
            data = {
                "success": True,
                "message": "new token generated successfully , expiry time is 5 minutes",
                "data": {
                    "access_token": serializer.validated_data.get("access")
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            # Customize the error response format
            error_data = {
                "message": "Token refresh failed",
                "status": "error",
                "errors": serializer.errors
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)