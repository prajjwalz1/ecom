from django.db import models
from django.utils import timezone
# from rest_framework.response import Response as RestResponse
from rest_framework.response import Response


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    

class CustomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def deleted(self):
        return super().get_queryset().filter(deleted_at__isnull=False)

class CustomizedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, editable=False)
    objects = CustomManager()
    all_objects = models.Manager()  

    def delete(self, hard=False, *args, **kwargs):
        if hard:
            super(CustomizedModel, self).delete(*args, **kwargs)
        else:
            self.deleted_at = timezone.now()
            super(CustomizedModel, self).save(*args, **kwargs)

    def restore(self):
        """Restore a soft-deleted record."""
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save()

    class Meta:
        ordering = ['created_at'] 
        abstract = True
        indexes = [
            models.Index(fields=['deleted_at']),
        ]
        

class ResponseMixin:
    """
    Handles Both Error and Successfull response
    """
    @staticmethod
    def handle_error_response(error_message, status_code):
        return Response(
            {"success": False, "message": str(error_message)},
            status=status_code,
        )
    @staticmethod
    def handle_serializererror_response(serializer_errors, status_code):
        # Combine all error messages into a single response structure
        error_messages = []
        for field, messages in serializer_errors.items():
            for message in messages:
                error_messages.append(f"{field}: {message}")

        return Response(
            {"success": False, "errors": error_messages},
            status=status_code,
        )

    @staticmethod
    def handle_success_response(status_code, serialized_data=None, message=None):
        response = {"success": True}
        

        if message:
            response["message"] = message
        if serialized_data:
            response["data"] = serialized_data
        else:
            response["data"] = []
        return Response(
            response,
            status=status_code,
        )
    def handle_paginated_response( status_code, serialized_data=None, message=None, page_obj=None):
        response = {"success": True}

        if message:
            response["message"] = message

        if serialized_data:
            response["data"] = serialized_data
        else:
            response["data"] = []

        # Add pagination info if page_obj is provided
        if page_obj:
            response["pagination"] = {
                "count": page_obj.paginator.count,
                "total_pages": page_obj.paginator.num_pages,
                "current_page": page_obj.number,  # Correctly reflect the current page
                "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
                "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
            }

        return Response(
            response,
            status=status_code,
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
        
