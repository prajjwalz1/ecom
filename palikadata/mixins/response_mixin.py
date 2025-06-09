from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

# from rest_framework.response import Response as RestResponse
from rest_framework.response import Response


class ResponseMixin:
    """
    Handles both error and successful responses.
    """

    @staticmethod
    def handle_error_response(error_message, status_code):
        return Response(
            {"success": False, "message": str(error_message)},
            status=status_code,
        )

    @staticmethod
    def handle_serializererror_response(serializer_errors, status_code):
        error_messages = [
            f"{field}: {msg}"
            for field, messages in serializer_errors.items()
            for msg in messages
        ]
        return Response(
            {"success": False, "errors": error_messages},
            status=status_code,
        )

    @staticmethod
    def handle_success_response(status_code, serialized_data=None, message=None):
        return Response(
            {
                "success": True,
                "message": message or "Request completed successfully",
                "data": serialized_data or [],
            },
            status=status_code,
        )

    def get_paginated_response_with_custom_format(self, data, message=None):
        assert self.paginator is not None, (
            "get_paginated_response_with_custom_format called without paginator. "
            "Did you forget to set pagination_class?"
        )

        return Response(
            {
                "success": True,
                "message": message or "Request completed successfully",
                "data": data,
                "pagination": {
                    "count": self.paginator.page.paginator.count,
                    "total_pages": self.paginator.page.paginator.num_pages,
                    "current_page": self.paginator.page.number,
                    "next_page": self.paginator.get_next_link(),
                    "previous_page": self.paginator.get_previous_link(),
                },
            }
        )


class GetSingleObjectMixin:
    """
    Fetches single object of given model using PK
    """

    def get_object(self, model_class, **kwargs):
        if not kwargs:
            return None, "At least one key-value pair must be provided."
        key, value = next(iter(kwargs.items()), (None, None))

        if key is None or value is None:
            return None, "Key and value must be provided."

        try:
            return model_class.objects.get(**{key: value}), None
        except model_class.DoesNotExist:
            return None, f"Item with {key} '{value}' does not exist."
        except Exception as e:
            return None, str(e)
