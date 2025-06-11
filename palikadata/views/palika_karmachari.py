from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.models.palika_karmachari import PalikaKarmachari
from palikadata.permissions.org_staff import IsPalikaAdmin, IsSamePalikaKarmachari
from palikadata.serializers.palika_karmachari import PalikaKarmachariSerializer


class PalikaKarmachariAPIView(APIView):
    authentication_classes = [JWT]
    permission_classes = [IsAuthenticated, IsPalikaAdmin]

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

        serializer = PalikaKarmachariSerializer(
            karmachari, data=request.data, partial=True
        )
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
