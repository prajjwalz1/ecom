from rest_framework import serializers

from palikadata.models.palika_karmachari import (
    PalikaKarmachari,  # Assuming your user model is here
)
from palikadata.serializers.local_government import (
    LocalGovernmentSerializer,  # Adjust import path as needed
)
from palikadata.serializers.sakha_serializer import PalikaSakhaSerializer
from user.serializers import UserSerializer  # Adjust import path as needed


class PalikaKarmachariSerializer(serializers.ModelSerializer):
    palika = LocalGovernmentSerializer()
    palika_sakha = PalikaSakhaSerializer()
    user = UserSerializer()

    class Meta:
        model = PalikaKarmachari
        fields = "__all__"


class PalikaKarmachariAssignSerializer(serializers.ModelSerializer):

    class Meta:
        model = PalikaKarmachari
        fields = "__all__"
