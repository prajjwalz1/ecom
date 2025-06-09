from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.mixins.palikafiltration_logic import OrgDeptQuerysetMixin
from palikadata.mixins.response_mixin import ResponseMixin
from palikadata.models.palika_program import PalikaProgram, PalikaProgramDocument
from palikadata.serializers.palika_program import (
    PalikaProgramDocumentSerializer,
    localgovProgramSerializer,
)


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


class ProgramApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWT]  # Use default authentication

    def post(self, request, *args, **kwargs):
        program_id = request.GET.get("program_id")  # Get program ID from query params
        action = request.GET.get("action")  # "approve" or "complete"

        if not program_id or action not in ["approve", "complete"]:
            return Response(
                {
                    "detail": "Program ID and valid action ('approve' or 'complete') required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            program = PalikaProgram.objects.get(id=program_id)
        except PalikaProgram.DoesNotExist:
            return Response(
                {"detail": "Palika Program not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get user's karmachari details
        karmachari_qs = request.user.karmachari_details.filter(is_admin=True)

        # Filter only if their palika matches the program's local_government
        karmachari = karmachari_qs.filter(palika=program.local_government).first()

        if not karmachari:
            return Response(
                {"detail": "You are not authorized to approve this program."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if action == "approve":
            if program.is_approved:
                return Response(
                    {"detail": "Program is already approved."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            program.is_approved = True
            program.approved_by = karmachari

        elif action == "complete":
            if program.is_completed_approved:
                return Response(
                    {"detail": "Program is already marked as completed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            program.is_completed_approved = True
            program.completed_approved_by = karmachari

        program.save()

        return Response(
            {"detail": f"Program successfully {action}d.", "program_id": program.id},
            status=status.HTTP_200_OK,
        )


class ProgramDocumentViewSet(ResponseMixin, OrgDeptQuerysetMixin, APIView):
    """
    A viewset for handling program documents.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWT]  # Use default authentication

    def get(self, request, *args, **kwargs):
        try:
            palika_program_id = kwargs.get("pk")
            if not palika_program_id:
                return self.handle_error_response(
                    status_code=400,
                    error_message="Palika Program ID is required.",
                )

            palika_program_docs = PalikaProgramDocument.objects.filter(
                palika_program__id=palika_program_id
            )
            # serialzier=\
            filtered_queryset = self.get_filtered_queryset(palika_program_docs)

            serialzier = PalikaProgramDocumentSerializer(
                filtered_queryset, many=True, context={"request": request}
            )
            return self.handle_success_response(
                status_code=200,
                serialized_data=serialzier.data,
                message="Documents fetched successfully",
            )
        except PalikaProgram.DoesNotExist:
            return self.handle_error_response(
                status_code=404,
                error_message="Palika Program not found.",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=500,
                error_message=f"An error occurred: {str(e)}",
            )

    def post(self, request, *args, **kwargs):
        try:
            palika_program_id = kwargs.get("pk")

            if not palika_program_id:
                return self.handle_error_response(
                    status_code=400,
                    error_message="Palika Program ID is required.",
                )

            # Fetch the program and check existence
            try:
                palika_program = PalikaProgram.objects.get(id=palika_program_id)
            except PalikaProgram.DoesNotExist:
                return self.handle_error_response(
                    status_code=404,
                    error_message="Palika Program not found.",
                )

            # Restriction: Only allow if user's organization and sakha match the program
            user = request.user
            karmachari_details = getattr(user, "karmachari_details", None)
            if not karmachari_details.exists():
                return self.handle_error_response(
                    status_code=403,
                    error_message="User does not have sakha/organization details.",
                )
            karmachari_detail = karmachari_details.first()
            user_org_id = getattr(karmachari_detail, "organization_id", None)
            user_sakha = (
                karmachari_detail.sakha.first()
                if karmachari_detail.sakha.exists()
                else None
            )
            user_sakha_id = user_sakha.id if user_sakha else None

            if (
                str(palika_program.local_government_id) != str(user_org_id)
                or str(palika_program.related_sakha_id) != str(user_sakha_id)
            ) and not karmachari_detail.is_admin:
                return self.handle_error_response(
                    status_code=403,
                    error_message="You do not have permission to add documents to this program.",
                )

            # Validate and save document
            serializer = PalikaProgramDocumentSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(palika_program=palika_program)
                return self.handle_success_response(
                    status_code=201,
                    serialized_data=serializer.data,
                    message="Document added successfully",
                )
            else:
                return self.handle_error_response(
                    status_code=400,
                    error_message=serializer.errors,
                )
        except Exception as e:
            return self.handle_error_response(
                status_code=500,
                error_message=f"An error occurred: {str(e)}",
            )
