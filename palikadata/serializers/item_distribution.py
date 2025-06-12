from rest_framework import serializers

from palikadata.models.record import DistributionDocument, LocalResident, Records


class DistributionItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    class Meta:
        model = Records
        fields = "__all__"


class DistributionDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    class Meta:
        model = DistributionDocument
        fields = "__all__"


class DistributionRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    class Meta:
        model = Records
        fields = "__all__"
