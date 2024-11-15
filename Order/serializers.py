from .models import ShippingDetails,Order,OrderItem,PaymentProof
from rest_framework import serializers


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model=ShippingDetails
        fields="__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields="__all__"


class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProof
        fields = ['order', 'image', 'payment_note']