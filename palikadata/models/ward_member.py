from django.db import models

from palikadata.views.mixins.mixins import CustomizedModel
from palikadata.models.local_government import LocalGovernment
from palikadata.models.ward import Ward


class WardPosition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ward Position"
        verbose_name_plural = "Ward Positions"


class PositionTenure(CustomizedModel):

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ward_position", "start_date"],
                name="unique_ward_position_tenure",
            )
        ]

    def __str__(self):
        return f"({self.start_date} - {self.end_date})"


class WardMember(CustomizedModel):
    local_government = models.ForeignKey(
        LocalGovernment, on_delete=models.PROTECT, related_name="ward_members"
    )
    ward = models.ForeignKey(
        Ward, on_delete=models.PROTECT, related_name="ward_members"
    )

    ward_position = models.ForeignKey(
        WardPosition, on_delete=models.PROTECT, related_name="ward_members"
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="ward_members", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    position_tenure = models.ForeignKey(
        PositionTenure,
        on_delete=models.PROTECT,
        related_name="ward_members",
        blank=True,
        null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ward", "local_government", "WardPosition"],
                name="unique_ward_gov_position",
            )
        ]
