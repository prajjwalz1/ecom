from rest_framework import serializers

from palikadata.models.palika_karmachari import (
    PalikaKarmachari,  # Assuming your user model is here
)


class PalikaKarmachariSerializer(serializers.ModelSerializer):
    class Meta:
        model = PalikaKarmachari
        fields = "__all__"
