from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.mixins.palikafiltration_logic import OrgDeptQuerysetMixin
from palikadata.mixins.response_mixin import ResponseMixin
from palikadata.models.palika_program import PalikaProgram, PalikaProgramDocument
from palikadata.pagination import StandardResultsSetPagination
from palikadata.permissions.org_staff import IsSamePalikaKarmachari
from palikadata.serializers.palika_program import (
    LocalGovProgramSerializer,
    PalikaProgramDocumentSerializer,
    PalikaProgramDocumentUploadSerializer,
)


class GovernmentProgramAPIView(ResponseMixin, OrgDeptQuerysetMixin, APIView):
    """
    An APIView for viewing and editing PalikaProgram instances.
    """

    permission_classes = [IsAuthenticated, IsSamePalikaKarmachari]
    authentication_classes = [JWT]

    def get_user_sakha_id(self, user):

        details = user.karmachari_details.last()
        sakha = details.palika_sakha
        return sakha.id if sakha else None

    def get_queryset(self, request):
        """
        Helper method to build a filtered queryset from query parameters.
        """
        queryset = PalikaProgram.objects.all()
        payload_local_government_id = request.query_params.get("local_government")
        sakha_id = request.query_params.get("sakha_id")
        search_query = request.query_params.get("search", "").strip()

        if payload_local_government_id:
            queryset = queryset.filter(local_government_id=payload_local_government_id)
        if sakha_id:
            queryset = queryset.filter(related_sakha=sakha_id)
        if search_query:
            queryset = queryset.filter(program_name__icontains=search_query)

        return queryset

    def get(self, request, *args, **kwargs):
        local_gov_id = request.query_params.get("local_government")
        if not local_gov_id:
            return self.handle_error_response(
                status_code=400,
                error_message="Local Government ID is required to retrieve programs.",
            )

        program_id = request.query_params.get("program_id")

        if program_id:
            try:
                instance = get_object_or_404(PalikaProgram, pk=program_id)

                program_sakha_id = getattr(instance, "related_sakha_id", None)
                karmachari_sakha_id = self.get_user_sakha_id(request.user)
                is_admin = getattr(
                    request.user.karmachari_details.first(), "is_admin", False
                )
                print(program_sakha_id, karmachari_sakha_id, is_admin)
                if (
                    program_sakha_id
                    and karmachari_sakha_id
                    and str(program_sakha_id) != str(karmachari_sakha_id)
                    and not is_admin
                ):
                    return self.handle_error_response(
                        status_code=403,
                        error_message="You do not have permission to access this Sakha's program.",
                    )

                serializer = LocalGovProgramSerializer(
                    instance, context={"request": request}
                )
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

        # List view
        sakha_id = request.query_params.get("sakha_id")
        # if not sakha_id:
        #     return self.handle_error_response(
        #         status_code=400,
        #         error_message="Please provide the Sakha ID to retrieve programs.",
        #     )

        # Sakha permission check
        karmachari_sakha_id = self.get_user_sakha_id(request.user)
        is_admin = getattr(request.user.karmachari_details.first(), "is_admin", False)
        if (
            sakha_id
            and karmachari_sakha_id
            and str(sakha_id) != str(karmachari_sakha_id)
            and not is_admin
        ):
            return self.handle_error_response(
                status_code=403,
                error_message="You do not have permission to access this Sakha's programs.",
            )

        queryset = self.get_queryset(request)

        # Paginate and serialize
        self.paginator = StandardResultsSetPagination()
        page = self.paginator.paginate_queryset(queryset, request)
        serializer = LocalGovProgramSerializer(
            page, many=True, context={"request": request}
        )

        return self.get_paginated_response_with_custom_format(
            data=serializer.data,
            message="Palika Programs fetched successfully",
        )

    def post(self, request, *args, **kwargs):
        serializer = LocalGovProgramSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return self.handle_success_response(
                status_code=201,
                serialized_data=serializer.data,
                message="Palika Program created successfully",
            )
        return self.handle_error_response(
            status_code=400,
            error_message=serializer.errors,
        )

    def patch(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if not pk:
            return self.handle_error_response(
                status_code=400,
                error_message="Program ID (pk) is required for update.",
            )
        try:
            instance = PalikaProgram.objects.get(pk=pk)
        except PalikaProgram.DoesNotExist:
            return self.handle_error_response(
                status_code=404,
                error_message="Palika Program not found.",
            )
        serializer = LocalGovProgramSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return self.handle_success_response(
                status_code=200,
                serialized_data=serializer.data,
                message="Palika Program updated successfully",
            )
        return self.handle_error_response(
            status_code=400,
            error_message=serializer.errors,
        )

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if not pk:
            return self.handle_error_response(
                status_code=400,
                error_message="Program ID (pk) is required for deletion.",
            )
        try:
            instance = PalikaProgram.objects.get(pk=pk)
            instance.delete()
            return self.handle_success_response(
                status_code=204,
                serialized_data=None,
                message="Palika Program deleted successfully",
            )
        except PalikaProgram.DoesNotExist:
            return self.handle_error_response(
                status_code=404,
                error_message="Palika Program not found.",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=400,
                error_message=f"Failed to delete Palika Program: {str(e)}",
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


class ProgramDocumentView(ResponseMixin, OrgDeptQuerysetMixin, APIView):
    """
    A viewset for handling program documents, with search feature.
    """

    permission_classes = [IsAuthenticated, IsSamePalikaKarmachari]
    authentication_classes = [JWT]  # Use default authentication

    def get(self, request):
        try:
            palika_program_id = request.query_params.get("palika_program_id")
            search_query = request.query_params.get("search", "").strip()
            karmachari = request.user.karmachari_details.first()
            user_org_id = getattr(karmachari, "palika", None).id
            user_sakha_id = getattr(karmachari, "palika_sakha", None)
            user_sakha_id = user_sakha_id.id if user_sakha_id else None

            if not user_org_id:
                return self.handle_error_response(
                    status_code=400,
                    error_message="User does not have a valid organization.",
                )

            queryset = PalikaProgramDocument.objects.all()

            if karmachari.is_admin:
                # Admin: fetch all documents for all programs of the local government
                queryset = queryset.filter(organization=user_org_id)
                if palika_program_id:
                    queryset = queryset.filter(palika_program_id=palika_program_id)
            else:
                # Non-admin: fetch only documents for programs user is associated to (org + sakha)
                queryset = queryset.filter(
                    organization=user_org_id,
                    department=user_sakha_id,
                )
                if palika_program_id:
                    queryset = queryset.filter(palika_program_id=palika_program_id)

            if search_query:
                queryset = queryset.filter(name__icontains=search_query)

            self.paginator = StandardResultsSetPagination()
            page = self.paginator.paginate_queryset(queryset, request)
            serializer = PalikaProgramDocumentSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response_with_custom_format(
                data=serializer.data,
                message="Documents fetched successfully",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=500,
                error_message=f"An error occurred: {str(e)}",
            )

    def post(self, request):
        try:
            # Get program
            try:
                palika_program = PalikaProgram.objects.get(
                    id=request.query_params.get("palika_program_id")
                )
            except PalikaProgram.DoesNotExist:
                return Response(
                    {"success": True, "message": "Palika Program not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get user’s karmachari details
            karmachari_qs = request.user.karmachari_details.first()
            if not karmachari_qs:
                return Response(
                    {
                        "success": False,
                        "message": "User does not have sakha/organization details.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            karmachari = karmachari_qs
            user_org_id = getattr(karmachari, "palika", None).id
            user_sakha = karmachari.palika_sakha
            user_sakha_id = user_sakha.id if user_sakha else None

            # Permissions: Must match organization AND sakha, unless is_admin
            if not karmachari.is_admin:
                if (
                    palika_program.local_government_id != user_org_id
                    or palika_program.related_sakha_id != user_sakha_id
                ):
                    return Response(
                        {
                            "success": False,
                            "message": "You do not have permission to add documents to this program.",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Multiple file uploads
            files = request.FILES.getlist("file")
            if not files:
                return Response(
                    {"success": False, "message": "No files provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            created_docs = []
            errors = []
            for file in files:
                data = {
                    "name": file.name,
                    "document": file,
                    "organization": user_org_id,
                    "department": user_sakha_id,
                    "palika_program": palika_program.id,
                }
                serializer = PalikaProgramDocumentUploadSerializer(
                    data=data, context={"request": request}
                )
                if serializer.is_valid():
                    serializer.save(palika_program=palika_program)
                    created_docs.append(serializer.data)
                else:
                    errors.append(serializer.errors)

            if created_docs:
                return Response(
                    {
                        "message": "Documents uploaded successfully.",
                        "documents": created_docs,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response({"detail": errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
