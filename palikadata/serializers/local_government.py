from rest_framework import serializers

from palikadata.models.local_government import LocalGovernment


class LocalGovernmentSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    class Meta:
        model = LocalGovernment
        fields = "__all__"
