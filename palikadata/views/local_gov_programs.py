from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.mixins import ResponseMixin
from palikadata.models.palika_program import PalikaProgram
from palikadata.serializers.palika_program import localgovProgramSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class GovernmentProgramViewSet(viewsets.ModelViewSet, ResponseMixin):
    """
    A viewset for viewing and editing PalikaProgram instances.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWT]  # Use default authentication

    queryset = PalikaProgram.objects.all()
    serializer_class = localgovProgramSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = PalikaProgram.objects.all()
        local_government_id = self.request.query_params.get("local_government")
        if local_government_id:
            queryset = queryset.filter(local_government_id=local_government_id)
        sakha_id = self.request.query_params.get("sakha_id")
        if sakha_id:
            queryset = queryset.filter(related_sakha=sakha_id)
            return queryset
        else:
            return queryset.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        sakha_id = request.query_params.get("sakha_id")
        if not sakha_id:
            return self.handle_error_response(
                status_code=400,
                error_message="Sakha ID is required to fetch Palika Programs.",
            )

        karmachari_sakha_details = self.request.user.karmachari_details.first()
        print(karmachari_sakha_details.is_admin)
        if karmachari_sakha_details:
            sakha = karmachari_sakha_details.sakha.first()
            karmachari_sakha_id = sakha.id if sakha else None
        if (
            sakha_id
            and karmachari_sakha_id
            and str(sakha_id) != str(karmachari_sakha_id)
            and not karmachari_sakha_details.is_admin
        ):
            return self.handle_error_response(
                status_code=403,
                error_message="You do not have permission to access this Sakha's programs.",
            )

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response_with_custom_format(
                data=serializer.data, message="Palika Programs fetched successfully"
            )

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
                message="Palika Program fetched successfully",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=400,
                error_message=f"Failed to fetch Palika Program: {str(e)}",
            )
