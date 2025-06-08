from django.contrib.auth.models import User
from django.db import models

from palikadata.mixins import CustomizedModel
from user.models import CustomUser


class PalikaKarmachari(CustomizedModel):
    """
    Model to represent a Palika Karmachari (Employee) within a local government.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="karmachari_details",
    )
    position = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="palika_karmachari/profile_pictures", null=True, blank=True
    )
    is_admin = models.BooleanField(default=False)
    palika = models.ForeignKey(
        "palikadata.LocalGovernment",
        on_delete=models.DO_NOTHING,
        related_name="karmachariharu",
        null=True,
    )
    palika_sakha = models.ForeignKey(
        "palikadata.PalikaSakha",
        on_delete=models.SET_NULL,
        related_name="karmacharis",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.first_name if self.user.first_name else str(None)
