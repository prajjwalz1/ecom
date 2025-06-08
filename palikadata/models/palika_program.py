from palikadata.models.local_government import LocalGovernment
from palikadata.models.palika_saakha import PalikaSakha
from palikadata.models.ward import Ward
from product.mixins import *


class PalikaProgram(CustomizedModel):
    local_government = models.ForeignKey(
        LocalGovernment, on_delete=models.PROTECT, related_name="palikaprograms"
    )
    ward = models.ForeignKey(
        "Ward",
        on_delete=models.PROTECT,
        related_name="wardprograms",
        null=True,
        blank=True,
    )
    budget_sirsak = models.CharField(
        max_length=255, null=True, blank=True
    )  # Budget Sirsaka (Budget Head)
    budget_sirsak_code = models.CharField(
        max_length=255, null=True, blank=True
    )  # Budget Sirsaka Code (Budget Head Code)
    budget_upa_sirsak = models.CharField(
        max_length=255, null=True, blank=True
    )  # Budget Upa Sirsaka (Sub Budget Head)
    budget_upa_sirsak_code = models.CharField(
        max_length=255, null=True, blank=True
    )  # Budget Upa Sirsaka Code (Sub Budget Head Code)
    program_name = models.CharField(max_length=255, null=False, blank=False)
    program_code = models.CharField(
        max_length=255, null=False, blank=False, unique=True
    )
    program_budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    program_description = models.TextField(null=True, blank=True)
    program_start_date = models.DateField(null=True, blank=True)
    program_end_date = models.DateField(null=True, blank=True)
    program_status = models.CharField(
        max_length=50,
        choices=(
            ("ongoing", "Ongoing"),
            ("completed", "Completed"),
            ("suspended", "Suspended"),
            ("not_started", "Not Started"),
        ),
        default="not_started",
    )
    related_sakha = models.ForeignKey(
        "PalikaSakha",
        on_delete=models.PROTECT,
        related_name="related_programs",
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.program_name}- {self.local_government.name}"
            if self.program_name
            else str(None)
        )

    class Meta:
        verbose_name = "Palika Program"
        verbose_name_plural = "Palika Programs"
