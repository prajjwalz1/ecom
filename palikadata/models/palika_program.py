import nepali_datetime
from django.utils import timezone

from palikadata.mixins.palikamodelmixin import PalikaSakhaBaseModel
from palikadata.models.local_government import LocalGovernment
from palikadata.models.palika_saakha import PalikaSakha
from palikadata.models.ward import Ward
from product.mixins import *


class FiscalYear(models.Model):
    """
    Model to represent a fiscal year.
    Bikram Sambat fiscal year: If month > 3 (i.e., after Chaitra), fiscal year is current year/next year.
    If month <= 3 (i.e., Chaitra or before), fiscal year is previous year/current year.
    """

    year = models.CharField(max_length=9, unique=True)  # e.g., "2078/79"
    is_current = models.BooleanField(
        default=False, help_text="Indicates if this is the current fiscal year."
    )

    def __str__(self):
        return self.year

    class Meta:
        verbose_name = "Fiscal Year"
        verbose_name_plural = "Fiscal Years"


class PalikaProgramDocument(CustomizedModel, PalikaSakhaBaseModel):
    palika_program = models.ForeignKey(
        "PalikaProgram", on_delete=models.CASCADE, related_name="program_documents"
    )

    name = models.CharField(max_length=255)
    document = models.FileField(
        upload_to="palika_program_documents/", null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.PROTECT,
        related_name="fiscal_year_programs",
        null=True,
        blank=True,
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Indicates if the program has been approved by the local government.",
    )
    approved_by = models.ForeignKey(
        "palikadata.PalikaKarmachari",
        on_delete=models.SET_NULL,
        related_name="approved_programs",
        null=True,
        blank=True,
    )
    is_completed_approved = models.BooleanField(
        default=False, help_text="Indicates if the program has been completed."
    )
    completed_approved_by = models.ForeignKey(
        "palikadata.PalikaKarmachari",
        on_delete=models.SET_NULL,
        related_name="completed_programs",
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.program_name}- {self.local_government.name}"
            if self.program_name
            else str(None)
        )

    def get_all_documents(self):
        """
        Returns all documents related to this PalikaProgram.
        """
        return self.program_documents.all()

    class Meta:
        verbose_name = "Palika Program"
        verbose_name_plural = "Palika Programs"
