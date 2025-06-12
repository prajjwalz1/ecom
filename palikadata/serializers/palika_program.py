from rest_framework import serializers

from palikadata.models.palika_program import (
    FiscalYear,
    PalikaProgram,
    PalikaProgramDocument,
)
from palikadata.serializers.local_government import LocalGovernmentSerializer


class FiscalYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalYear
        fields = "__all__"


class LocalGovProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    fiscal_year = FiscalYearSerializer(read_only=True, source="fical_year")

    class Meta:
        model = PalikaProgram
        fields = "__all__"


class PalikaProgramDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgramDocument model.
    """

    palika_program = LocalGovProgramSerializer(read_only=True)
    organization = LocalGovernmentSerializer(source="palika_program.local_government")

    class Meta:
        model = PalikaProgramDocument
        fields = "__all__"


class PalikaProgramDocumentUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgramDocument model.
    """

    class Meta:
        model = PalikaProgramDocument
        fields = "__all__"
