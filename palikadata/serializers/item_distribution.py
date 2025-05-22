from rest_framework import serializers

from palikadata.models.distribution import (
    DistributionDocument,
    DistributionItem,
    DistributionRecord,
)


class DistributionItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    class Meta:
        model = DistributionItem
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
        model = DistributionRecord
        fields = "__all__"
