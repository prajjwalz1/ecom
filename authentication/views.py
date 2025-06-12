from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from product.mixins import ResponseMixin
from product.models import Brand, Category, Tag
from product.serializers import BrandSerializer, CategorySerializer, GetTagSerializer

User = get_user_model()
from palikadata.utils.user_organization_and_org_id import GetUserOrganizationAndOrgId


# Create your views here.
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class CustomTokenObtainView(APIView, ResponseMixin):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Serialize incoming data
        serializer = CustomAuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            # Authenticate user manually
            try:
                user = User.objects.get(email=email)
            except Exception as e:
                return self.handle_error_response(
                    error_message=f"no user found with the given email{e}",
                    status_code=400,
                )

            if not user.check_password(password):
                return self.handle_error_response(
                    error_message="invalid password", status_code=400
                )

            # if user.is_authenticated:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Return tokens in custom format
            try:
                user_related_palika_project_data = (
                    GetUserOrganizationAndOrgId.get_user_organization_id(user)
                )
            except Exception as e:
                user_related_palika_project_data = {
                    "message": "No organization found for this user",
                    "error": str(e),
                    "success": False,
                }
            # Prepare response data
            response_data = {
                "success": True,
                "message": "logged in successfully",
                "access_token": access_token,
                "refresh_token": str(refresh),
                "palika_data": user_related_palika_project_data,
            }

            return Response(response_data)

            return Response(
                {
                    "status": "error",
                    "message": "Invalid credentials",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # If serializer is invalid, return error
        return Response(
            {
                "status": "error",
                "message": "Invalid data",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


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
                "data": {"access_token": serializer.validated_data.get("access")},
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            # Customize the error response format
            error_data = {
                "message": "Token refresh failed",
                "status": "error",
                "errors": serializer.errors,
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Optionally, add custom logic here
        try:
            response = super().post(request, *args, **kwargs)
            # Custom response modification (if needed)
            data = response.data
            print(data)
            data["message"] = "Token refreshed successfully"
            # return Response(data, status=response.status_code)
            data = {
                "success": True,
                "message": "new token generated successfully , expiry time is 5 minutes",
                "data": {"access_token": data.get("access")},
            }
            return Response(data)
        except Exception as e:
            return Response(
                {"success": False, "message": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
