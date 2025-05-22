from django.shortcuts import render
from rest_framework import permissions, viewsets

from palikadata.mixins import ResponseMixin
from palikadata.models.local_government import LocalGovernment
from palikadata.permissions.superuser import IsSuperUser
from palikadata.serializers.local_government import LocalGovernmentSerializer


# Create your views here.
class LocalGovernmentViewSet(viewsets.ModelViewSet, ResponseMixin):
    queryset = LocalGovernment.objects.all()
    serializer_class = LocalGovernmentSerializer

    admin_request_only = [
        "POST",
        "PATCH",
        "ADD",
        "UPDATE",
    ]  # you can add any requets_type ein this

    def get_authenticators(self):
        request_type = self.request.GET.get("request_type", "").upper()
        method = self.request.method.upper()

        if method in self.admin_request_only or request_type in self.admin_request_only:
            return super().get_authenticators()
        return []  # Skip authentication for others

    def get_permissions(self):
        request_type = self.request.GET.get("request_type", "").upper()
        method = self.request.method.upper()

        if method in self.admin_request_only or request_type in self.admin_request_only:
            return [IsSuperUser()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.handle_success_response(
            status_code=200,
            serialized_data=serializer.data,
            message="Palika Programs fetched successfully",
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.handle_success_response(
                status_code=200,
                serialized_data=serializer.data,
                message="local government fetched successfully",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=400,
                error_message=f"Failed to government data: {str(e)}",
            )
