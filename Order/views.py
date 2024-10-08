from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from product.mixins import *
from .serializers import ShippingSerializer,OrderSerializer
from .models import *
# Create your views here.
from django.db import transaction
from django.shortcuts import get_object_or_404

import datetime
import random

def generate_order_id():
    # Get the current date and time
    now = datetime.datetime.now()
    # Format date and time in the desired format (e.g., YYYYMMDDHHMMSS)
    timestamp = now.strftime("%Y%m%d")
    # Generate a random number between 1000 and 9999
    random_num = random.randint(1000, 9999)
    # Combine timestamp and random number to create a unique order ID
    order_id = f"{timestamp}{random_num}"
    return order_id

class CheckOut(APIView,ResponseMixin):


    def post(self,request):
        request_type=request.GET.get("request")
        if request_type=="create_checkout":
            return self.create_checkout(request)
    def create_checkout(self,request):
        shipping_details_data = request.data.get("shippingDetails")
        cart = request.data.get("cart")
        order_id = generate_order_id()
        
        # Initialize cart amount
        cart_amount = 0
        promotional_discount = 0
        price_after_discount = 0
        promocode = None

        # Calculate the cart amount and determine promo code discount
        for item in cart:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            # Fetch the product to get the price
            product = get_object_or_404(Product, id=product_id)
            cart_amount += product.price * quantity

        # Apply promo code if provided
        promo_code_data = request.data.get("promo_code")
        if promo_code_data:
            promocode = get_object_or_404(PromoCode, code=promo_code_data)
            promotional_discount = promocode.calculate_discount(cart_amount)  # Assuming a method that calculates discount
            price_after_discount = cart_amount - promotional_discount
        else:
            price_after_discount = cart_amount

        # Create the Order object
        order = Order.objects.create(
            orderid=order_id,
            cart_amount=cart_amount,
            promotional_discount=promotional_discount,
            promocode_used=promocode,
            price_after_discount=price_after_discount,
        )

        # Attach the order object to the shipping details data
        shipping_details_data["order"] = order.id

        # Create OrderItem instances
        order_items = []
        with transaction.atomic():
            for item in cart:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)
                
                product = get_object_or_404(Product, id=product_id)
                purchase_amount = product.price * quantity

                # Create an OrderItem instance and add it to the list
                order_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    purchase_amount=purchase_amount
                )
                order_items.append(order_item)

            # Bulk create the OrderItem objects for efficiency
            OrderItem.objects.bulk_create(order_items)

        # Save shipping details
        shipping_serializer = ShippingSerializer(data=shipping_details_data)
        if not shipping_serializer.is_valid():
            return self.handle_serializererror_response(error_messages=shipping_serializer.errors, status_code=400)
        shipping_serializer.save()

        return self.handle_success_response(status_code=200, message="Order created successfully",serialized_data={"order_id":order_id,"order_amount":cart_amount})
