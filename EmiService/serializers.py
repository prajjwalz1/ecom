from rest_framework import serializers
from .models import *

class EMIConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMIConfig
        fields = '__all__'

    def validate_tenure_months(self, value):
        """
        Validate tenure_months against allowed values.
        """
        loan_type = self.initial_data.get('loan_type')
        if loan_type:
            valid_tenures = LoanTenure.objects.filter(loan_type=loan_type).values_list('months', flat=True)
            if value not in valid_tenures:
                raise ValidationError(f"The tenure {value} months is not allowed for this loan type.")
        else:
            raise ValidationError("Loan type is required to validate tenure.")
        return value


class LoanTypeSerializer(serializers.ModelSerializer):
    months_tenures = serializers.SerializerMethodField()

    class Meta:
        model = LoanType
        fields = ['id', 'name','months_tenures', 'default_interest_rate', 'max_tenure_years', 'description']

    def get_months_tenures(self, obj):
        """
        Return a list of valid tenures (in months) for the loan type.
        """
        return LoanTenure.objects.filter(loan_type=obj).values_list('months', flat=True)