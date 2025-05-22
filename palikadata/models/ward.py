from django.db import models

from palikadata.mixins import CustomizedModel
from palikadata.models.local_government import LocalGovernment


class Ward(CustomizedModel):
    name = models.CharField(max_length=100)
    local_government = models.ForeignKey(
        LocalGovernment, on_delete=models.CASCADE, related_name="wards"
    )

    def __str__(self):
        return f"{self.name} ({self.local_government.name})"
