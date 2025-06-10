from rest_framework import serializers

from palikadata.models.palika_program import (
    FiscalYear,
    PalikaProgram,
    PalikaProgramDocument,
)


class PalikaProgramDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgramDocument model.
    """

    class Meta:
        model = PalikaProgramDocument
        fields = "__all__"


class FiscalYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalYear
        fields = "__all__"


class LocalGovProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    fiscal_year = FiscalYearSerializer(read_only=True, source="fical_year")
    documents = PalikaProgramDocumentSerializer(
        many=True, read_only=True, source="program_documents"
    )

    class Meta:
        model = PalikaProgram
        fields = "__all__"
