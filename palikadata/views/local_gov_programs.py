from django.shortcuts import render
from rest_framework import viewsets

from palikadata.mixins import ResponseMixin
from palikadata.models.palika_program import PalikaProgram
from palikadata.serializers.palika_program import localgovProgramSerializer


# Create your views here.
class GovernmentProgramViewSet(viewsets.ModelViewSet, ResponseMixin):
    """
    A viewset for viewing and editing PalikaData instances.
    """

    queryset = PalikaProgram.objects.all()
    serializer_class = localgovProgramSerializer

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
                message="Palika Program fetched successfully",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=400,
                error_message=f"Failed to fetch Palika Program: {str(e)}",
            )
