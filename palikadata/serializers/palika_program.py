from rest_framework import serializers

from palikadata.models.palika_program import PalikaProgram, PalikaProgramDocument


class PalikaProgramDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgramDocument model.
    """

    class Meta:
        model = PalikaProgramDocument
        fields = "__all__"


class localgovProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    documents = PalikaProgramDocumentSerializer(
        many=True, read_only=True, source="program_documents"
    )

    class Meta:
        model = PalikaProgram
        fields = "__all__"
