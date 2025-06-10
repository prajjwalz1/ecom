# serializers.py
from rest_framework import serializers

from palikadata.models.palika_karmachari import PalikaKarmachari
from palikadata.models.palika_saakha import PalikaSakha


class KarmaSakhaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PalikaKarmachari
        fields = "__all__"


class PalikaSakhaSerializer(serializers.ModelSerializer):
    sakha_pramukh = KarmaSakhaSerializer(allow_null=True, read_only=True)

    class Meta:
        model = PalikaSakha
        fields = "__all__"
