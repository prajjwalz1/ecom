# views.py
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.mixins.response_mixin import ResponseMixin
from palikadata.models.palika_karmachari import PalikaKarmachari
from palikadata.models.palika_saakha import PalikaSakha
from palikadata.pagination import StandardResultsSetPagination
from palikadata.permissions.org_staff import IsSamePalikaKarmachari
from palikadata.serializers.sakha_serializer import PalikaSakhaSerializer


class PalikaSakhaViewSet(ResponseMixin, viewsets.ModelViewSet):
    queryset = PalikaSakha.objects.all()
    serializer_class = PalikaSakhaSerializer
    authentication_classes = [JWT]
    permission_classes = [IsSamePalikaKarmachari]

    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):

        palika_id = request.data.get("local_government")
        if palika_id:
            try:
                user_karmachari = PalikaKarmachari.objects.get(
                    user=request.user, is_active=True
                )
                if str(user_karmachari.palika.id) != str(palika_id):
                    return self.handle_error_response(
                        status_code=403,
                        error_message="You do not have permission to create a PalikaSakha for this Palika.",
                    )
            except PalikaKarmachari.DoesNotExist:
                return self.handle_error_response(
                    error_message="palika not found", status_code=404
                )
        else:
            return self.handle_error_response(
                status_code=400,
                error_message="Palika ID is required to create a PalikaSakha.",
            )
        if not user_karmachari.is_admin:
            return self.handle_error_response(
                status_code=403,
                error_message="only admin can create the sakha.",
            )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return self.handle_serializererror_response(
                serializer.errors, status_code=400
            )
        self.perform_create(serializer)
        return self.handle_success_response(
            status_code=201,
            serialized_data=serializer.data,
            message="PalikaSakha created successfully",
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return self.handle_serializererror_response(
                serializer.errors, status_code=400
            )
        self.perform_update(serializer)
        return self.handle_success_response(
            status_code=200,
            serialized_data=serializer.data,
            message="PalikaSakha updated successfully",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.handle_success_response(
            status_code=204,
            serialized_data=None,
            message="PalikaSakha deleted successfully",
        )

    def list(self, request, *args, **kwargs):

        user = request.user
        karmachari_details = user.karmachari_details.all()

        for karmachari_detail in karmachari_details:
            user_palika = karmachari_detail.palika

            if user_palika:
                filtered_queryset = self.queryset.filter(palika=user_palika)
                break

        queryset = filtered_queryset

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response_with_custom_format(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.handle_success_response(
            status_code=200,
            serialized_data=serializer.data,
            message="PalikaSakha list fetched successfully",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.handle_success_response(
            status_code=200,
            serialized_data=serializer.data,
            message="PalikaSakha detail fetched successfully",
        )
