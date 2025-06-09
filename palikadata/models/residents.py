from django.db import models

from palikadata.mixins.datetimemodelmixin import CustomizedModel
from palikadata.models.local_government import LocalGovernment
from palikadata.models.ward import Ward


class LocalResident(CustomizedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=10,
        choices=(("male", "male"), ("female", "female"), ("other", "other")),
    )
    date_of_birth = models.DateField(blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    grandfather_name = models.CharField(max_length=100, blank=True, null=True)
    wife_name = models.CharField(max_length=100, blank=True, null=True)
    husband_name = models.CharField(max_length=100, blank=True, null=True)
    local_government = models.ForeignKey(
        LocalGovernment, on_delete=models.CASCADE, related_name="residents"
    )
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name="residents")
    tole = models.CharField(max_length=100, blank=True, null=True)
    citizenship_number = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    citizen_photo = models.ImageField(upload_to="residents", blank=True, null=True)
    nid = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    # other resident details (address, contact, etc.)

    def __str__(self):
        return self.first_name
