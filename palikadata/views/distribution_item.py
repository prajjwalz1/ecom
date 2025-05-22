from rest_framework import viewsets

from palikadata.mixins import ResponseMixin
from palikadata.models.distribution import DistributionItem
from palikadata.serializers.item_distribution import DistributionItemSerializer


class DistributionItemViewSet(viewsets.ModelViewSet, ResponseMixin):
    """
    A viewset for viewing and editing PalikaData instances.
    """

    queryset = DistributionItem.objects.all()
    serializer_class = DistributionItemSerializer

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

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return self.handle_success_response(
                status_code=201,
                serialized_data=serializer.data,
                message="Palika Program created successfully",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=400,
                error_message=f"Failed to create Palika Program: {str(e)}",
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return self.handle_success_response(
                status_code=200,
                serialized_data=serializer.data,
                message="Palika Program updated successfully",
            )
        except Exception as e:
            return self.handle_error_response(
                status_code=400,
                error_message=f"Failed to update Palika Program: {str(e)}",
            )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
