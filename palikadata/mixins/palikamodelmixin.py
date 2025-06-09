from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from palikadata.models.local_government import LocalGovernment
from palikadata.models.palika_saakha import PalikaSakha


class PalikaSakhaBaseModel(models.Model):
    """
    Abstract base model to be inherited by models related to Palika (LocalGovernment) and PalikaSakha.
    """

    organization = models.ForeignKey(
        LocalGovernment,
        on_delete=models.PROTECT,
        related_name="%(class)s_local_government",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        PalikaSakha,
        on_delete=models.PROTECT,
        related_name="%(class)s_related_sakha",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
