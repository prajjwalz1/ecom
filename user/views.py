from django.shortcuts import render

# Create your views here.
# users/views.py
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.mixins.response_mixin import ResponseMixin
from palikadata.pagination import StandardResultsSetPagination
from palikadata.permissions.org_staff import IsSamePalikaKarmachari

from .models import CustomUser
from .models import CustomUser as User
from .serializers import (
    RegisterUserSerializer,
    TokenObtainPairSerializer,
    UserSerializer,
)


class CustomUserViewSet(ResponseMixin, viewsets.ModelViewSet):
    authentication_classes = [JWT]
    permission_classes = [IsSamePalikaKarmachari]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Get the requesting user's palika (if they are a PalikaKarmachari)
        local_gov_id = self.request.GET.get("local_government")

        if not local_gov_id:
            return CustomUser.objects.none()

        # Filter users who are linked to a PalikaKarmachari in the same palika
        return CustomUser.objects.filter(
            karmachari_details__palika_id=local_gov_id,
            karmachari_details__is_active=True,
        ).distinct()

    # ─── LIST ───────────────────────────────────────────────────────────────────
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response_with_custom_format(
                data=ser.data, message="Users fetched successfully"
            )

        ser = self.get_serializer(qs, many=True)
        return self.handle_success_response(status.HTTP_200_OK, ser.data)

    # ─── CREATE ─────────────────────────────────────────────────────────────────
    def perform_create(self, serializer):
        # auto-assign creator
        print("Creating user with created_by:", self.request.user)
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if ser.is_valid():
            self.perform_create(ser)
            return self.handle_success_response(
                status.HTTP_201_CREATED,
                ser.data,
                message="User created successfully",
            )
        return self.handle_serializererror_response(
            ser.errors, status.HTTP_400_BAD_REQUEST
        )

    # ─── UPDATE (PUT) ───────────────────────────────────────────────────────────

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            password = request.data.get("password", None)
            if password:
                instance.set_password(password)
                instance.save()
                # Remove password from validated_data so serializer.save() won't overwrite it
                serializer.validated_data.pop("password", None)

            serializer.save()  # saves other fields except password now

            return self.handle_success_response(
                status.HTTP_200_OK,
                serializer.data,
                message="User updated successfully",
            )

        return self.handle_serializererror_response(
            serializer.errors, status.HTTP_400_BAD_REQUEST
        )

    # ─── PARTIAL UPDATE (PATCH) ─────────────────────────────────────────────────
    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     ser = self.get_serializer(instance, data=request.data, partial=True)
    #     if ser.is_valid():
    #         ser.save()
    #         return self.handle_success_response(
    #             status.HTTP_200_OK,
    #             ser.data,
    #             message="User partially updated successfully",
    #         )
    #     return self.handle_serializererror_response(
    #         ser.errors, status.HTTP_400_BAD_REQUEST
    #     )

    # ─── DESTROY ───────────────────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.handle_success_response(
            status.HTTP_204_NO_CONTENT,
            serialized_data=None,
            message="User deleted successfully",
        )


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]
