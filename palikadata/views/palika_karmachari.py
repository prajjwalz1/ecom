from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.mixins.response_mixin import ResponseMixin
from palikadata.models.palika_karmachari import PalikaKarmachari
from palikadata.pagination import (
    StandardResultsSetPagination,  # adjust the import path accordingly
)
from palikadata.permissions.org_staff import IsPalikaAdmin, IsSamePalikaKarmachari
from palikadata.serializers.palika_karmachari import PalikaKarmachariSerializer


class PalikaKarmachariAPIView(APIView, ResponseMixin):
    authentication_classes = [JWT]
    permission_classes = [IsAuthenticated, IsPalikaAdmin]
    pagination_class = StandardResultsSetPagination()

    def get(self, request):
        # Get the local government
        karmachari = request.user.karmachari_details.first()
        if not karmachari or not karmachari.palika:
            return self.handle_error_response(
                "User does not belong to any local government.",
                status.HTTP_400_BAD_REQUEST,
            )

        local_government = karmachari.palika
        queryset = PalikaKarmachari.objects.filter(palika=local_government)

        paginator = self.pagination_class
        page = paginator.paginate_queryset(queryset, request)
        serializer = PalikaKarmachariSerializer(
            page, many=True, context={"request": request}
        )

        # Inject paginator into self to match get_paginated_response_with_custom_format usage
        self.paginator = paginator
        return self.get_paginated_response_with_custom_format(
            data=serializer.data, message="Karmachari list fetched successfully."
        )

    def post(self, request):
        serializer = PalikaKarmachariSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Karmachari created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            karmachari = PalikaKarmachari.objects.get(pk=pk)
        except PalikaKarmachari.DoesNotExist:
            return Response(
                {"error": "Karmachari not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PalikaKarmachariSerializer(karmachari, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Karmachari updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            karmachari = PalikaKarmachari.objects.get(pk=pk)
        except PalikaKarmachari.DoesNotExist:
            return Response(
                {"error": "Karmachari not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PalikaKarmachariSerializer(
            karmachari, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Karmachari partially updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
