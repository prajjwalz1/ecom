
from django.db import models
from product.mixins import CustomizedModel
from django.core.exceptions import ValidationError  # Correct import for ValidationError


class LoanType(CustomizedModel):
    """
    Model to define different types of loans and their specific configurations.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Type of loan (e.g., 'aMAUNG FINANCE', 'aPPLE FINANCE').")
    default_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Default annual interest rate for this loan type.")
    max_tenure_years = models.PositiveIntegerField(help_text="Maximum tenure in years for this loan type.")
    description = models.TextField(blank=True, help_text="Optional description of the loan type.")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Loan Type"
        verbose_name_plural = "Loan Types"

class LoanTenure(models.Model):
    """
    Model to store valid loan tenures for different loan types.
    """
    loan_type = models.ForeignKey(
        LoanType, 
        on_delete=models.CASCADE, 
        related_name="valid_tenures", 
        help_text="Loan type to which this tenure belongs."
    )
    months = models.PositiveIntegerField(help_text="Tenure in months.")

    class Meta:
        unique_together = ('loan_type', 'months')
        ordering = ['loan_type', 'months']

    def __str__(self):
        return f"{self.loan_type.name} - {self.months} months"
    


class EMIConfig(models.Model):
    loan_type = models.ForeignKey(
        LoanType, 
        on_delete=models.CASCADE, 
        related_name="emi_configs"
    )
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.PositiveIntegerField(help_text="Loan tenure in months.")
    # Other fields...

    def clean(self):
        """
        Validate the tenure_months field against allowed tenures.
        """
        valid_tenures = LoanTenure.objects.filter(loan_type=self.loan_type).values_list('months', flat=True)
        if self.tenure_months not in valid_tenures:
            raise ValidationError({
                'tenure_months': f"The tenure {self.tenure_months} months is not allowed for this loan type."
            })

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation
        super().save(*args, **kwargs)
