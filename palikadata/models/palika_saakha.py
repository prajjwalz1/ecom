from django.db import models

from palikadata.mixins import CustomizedModel
from palikadata.models.palika_karmachari import PalikaKarmachari


class PalikaSakha(CustomizedModel):
    """
    Model to represent a Palika Sakha (Branch) within a local government.
    """

    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    sakha_pramukh = models.ForeignKey(
        PalikaKarmachari,
        on_delete=models.PROTECT,
        related_name="sakha",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name if self.name else str(None)


class PalikaSakhaPramukhHistory(CustomizedModel):
    """
    Model to keep history of sakha pramukh changes for a PalikaSakha.
    """

    palika_sakha = models.ForeignKey(
        PalikaSakha, on_delete=models.DO_NOTHING, related_name="pramukh_history"
    )
    sakha_pramukh = models.ForeignKey(
        PalikaKarmachari,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pramukh_history_records",
    )
    tenure_from = models.DateField(null=True, blank=True)
    tenure_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.palika_sakha.name} - {self.sakha_pramukh} at {self.tenure_to}"
