from rest_framework import serializers

from palikadata.models.palika_program import PalikaProgram


class localgovProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for PalikaProgram model.
    """

    class Meta:
        model = PalikaProgram
        fields = "__all__"
