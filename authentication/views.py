from django.contrib.auth import authenticate
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from product.mixins import ResponseMixin
from django.contrib.auth import get_user_model, authenticate
from product.models import Category,Brand,Tag
from product.serializers import BrandSerializer,CategorySerializer,GetTagSerializer
User = get_user_model()
# Create your views here.
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class CustomTokenObtainView(APIView,ResponseMixin):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        # Serialize incoming data
        print(request.data)
        serializer = CustomAuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Authenticate user manually
            try:
                user = User.objects.get(email=email)
            except Exception as e:
                return self.handle_error_response(error_message="no user found with the given email",status_code=400)

            if not user.check_password(password):
                return self.handle_error_response(error_message="invalid password",status_code=400)


            
            # if user.is_authenticated:
                # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Return tokens in custom format
            categories = Category.objects.all()
            brands = Brand.objects.all()
            tags = Tag.objects.all()

            # Serialize related data
            categories_data = CategorySerializer(categories, many=True).data
            brands_data = BrandSerializer(brands, many=True).data
            tags_data = GetTagSerializer(tags, many=True).data

            # Prepare response data
            response_data = {
                "success":True,
                "message":"logged in successfully",
                'access': access_token,
                'refresh': str(refresh),
                'categories': categories_data,
                'brands': brands_data,
                'tags': tags_data
            }

            return Response(response_data)
            
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