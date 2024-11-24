from .models import *
from rest_framework import serializers


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model=ShippingDetails
        fields="__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields="__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Replace the product ID with the product_name
        # Assuming that the `OrderItem` model has a ForeignKey relationship to `Product` named `product`
        representation['product'] = instance.product.product_name
        representation['product_variant'] = instance.product.product_name
        representation['product_color'] = instance.product_color
        
        return representation



class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProof
        fields = ['id','image', 'payment_note']
    

class ApplyPromoCodeSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    promo_code = serializers.CharField()


class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'

class OrderGenericsSerializer(serializers.ModelSerializer):
    shippingdetails = ShippingSerializer()
    orderitems=OrderItemSerializer(many=True)
    class Meta:
        model=Order
        fields="__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        payment_slip = instance.qr_payment_slip
        request = self.context.get("request")  # Access the request
        if payment_slip and payment_slip.image:
            representation['qr_payment_slip'] = (
                request.build_absolute_uri(payment_slip.image.url)
                if request else payment_slip.image.url
            )
        else:
            representation['qr_payment_slip'] = None

        # representation["ordered_by"]=   instance.shippingdetails.fullname if instance.shippingdetails else None
        return representation
    

    def update(self, instance, validated_data):
        """
        Override the update method to update the nested shippingdetails fields.
        """
        # Extract shippingdetails from validated data if present
        shippingdetails_data = validated_data.pop('shippingdetails', None)
        print(shippingdetails_data)

        # Update the main order instance with validated fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # If shippingdetails data is provided, update the related ShippingDetails model
        if shippingdetails_data:
            # Check if the related ShippingDetails instance exists
            if instance.shippingdetails:
                # Update the existing shippingdetails
                for attr, value in shippingdetails_data.items():
                    setattr(instance.shippingdetails, attr, value)
                instance.shippingdetails.save()
            else:
                # If no related ShippingDetails instance, create one (optional)
                instance.shippingdetails = ShippingDetails.objects.create(**shippingdetails_data)

        instance.save()  # Save the updated order instance
        return instance