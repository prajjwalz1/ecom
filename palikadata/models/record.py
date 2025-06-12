from django.db import models

from palikadata.mixins.datetimemodelmixin import CustomizedModel
from palikadata.models.local_government import LocalGovernment
from palikadata.models.residents import LocalResident
from palikadata.models.ward import Ward


class ActionType(CustomizedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DistributionItem(CustomizedModel):
    under_program = models.ForeignKey(
        "PalikaProgram", on_delete=models.CASCADE, related_name="distribution_items"
    )
    item_name = models.CharField(
        max_length=100
    )  # e.g. Food package, Medicine, Cash aid, etc.

    def __str__(self):
        return self.item_name


class DistributionDocument(CustomizedModel):

    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to="distribution_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document_name


class Records(CustomizedModel):
    action = models.ForeignKey(
        ActionType, on_delete=models.PROTECT, related_name="distribution_records"
    )
    program = models.ForeignKey(
        "PalikaProgram", on_delete=models.CASCADE, related_name="distribution_records"
    )

    extra_data = models.JSONField(blank=True, null=True)

    local_government = models.ForeignKey(
        LocalGovernment, on_delete=models.PROTECT, related_name="distributions"
    )
    ward = models.ForeignKey(
        Ward, on_delete=models.PROTECT, related_name="distributions"
    )
    resident = models.ForeignKey(
        LocalResident, on_delete=models.PROTECT, related_name="distributions"
    )
    item = models.ForeignKey(DistributionItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    distribution_date = models.DateField(blank=True, null=True)
    distribution_document = models.ForeignKey(
        DistributionDocument,
        on_delete=models.PROTECT,
        related_name="distribution_records",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.quantity} x {self.item.item_name} to {self.resident.first_name} ({self.ward.name}, {self.local_government.name})"
