from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


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
        ordering = ["created_at"]
        abstract = True
        indexes = [
            models.Index(fields=["deleted_at"]),
        ]
