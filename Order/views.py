from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from product.mixins import *
from .serializers import ShippingSerializer,OrderSerializer,PaymentProofSerializer
from .models import *
# Create your views here.
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import render
import datetime
import random
from django.views import View
import base64
import json
from decimal import Decimal
from rest_framework.views import APIView 
from django.http import JsonResponse
from product.mixins import ResponseMixin
from rest_framework.decorators import api_view
from django.conf import settings
import os
from product.models import ProductVariant

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
    def generate_transaction_id(self,order_id):
        """
        Generates a transaction ID in the format "infotech-order-<order_id>".

        Args:
            order_id (str): The order ID to include in the transaction ID.

        Returns:
            str: The generated transaction ID.
        """
        # Ensure order_id is a string
        order_id_str = str(order_id)

        # Construct the transaction ID
        transaction_id = f"infotech-order-{order_id_str}"
        
        return transaction_id

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
        product_ids = {item.get("product_id") for item in cart}
        variant_ids = {item.get("product_variant_id") for item in cart if item.get("product_variant_id")}

        # Fetch all products and variants at once
        products = Product.objects.filter(id__in=product_ids)
        variants = ProductVariant.objects.filter(id__in=variant_ids)

        # Create dictionaries for quick lookup by ID
        # product_price_map = {product.id: product.price for product in products}
        variant_price_map = {variant.id: variant.discount_price for variant in variants}

        # Calculate cart amount
        cart_amount = 0
        for item in cart:
            product_id = item.get("product_id")
            variant_id = item.get("product_variant_id")
            quantity = item.get("quantity", 1)
            
            # Use variant price if available; otherwise, fallback to product price
            price = variant_price_map.get(variant_id)
            cart_amount += price * quantity

        # Apply promo code if provided
        promo_code_data = request.data.get("promo_code")
        if promo_code_data:
            promocode = get_object_or_404(PromoCode, code=promo_code_data)
            promotional_discount = promocode.calculate_discount(cart_amount)  # Assuming a method that calculates discount
            price_after_discount = cart_amount - promotional_discount
        else:
            price_after_discount = cart_amount
        print(price_after_discount)
        # Create the Order object
        tranx_id=self.generate_transaction_id(order_id)
        order = Order.objects.create(
            orderid=order_id,
            cart_amount=cart_amount,
            promotional_discount=promotional_discount,
            promocode_used=promocode,
            price_after_discount=price_after_discount,
            transaction_uuid=tranx_id
        )

        # Attach the order object to the shipping details data
        shipping_details_data["order"] = order.id

        # Create OrderItem instances
        order_items = []
        with transaction.atomic():
            for item in cart:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)
                variant_id=item.get("product_variant_id")
                
                product = get_object_or_404(Product, id=product_id)
                purchase_amount = variant_price_map.get(variant_id)

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
        serializer = ShippingSerializer(data=shipping_details_data)
        if not serializer.is_valid():
            return self.handle_serializererror_response(serializer.errors, status_code=400)
        serializer.save()

        return self.handle_success_response(status_code=200, message="Order created successfully",serialized_data={"order_id":order_id,"order_amount":cart_amount,"transaction_uuid":tranx_id})




class eSewaSuccessView(View):
    def get(self, request):
        # Get the encoded data from the query parameter
        encoded_data = request.GET.get('data')
        frontend_url=os.environ.get("NEXT_BASE_URL")

        if encoded_data:
            try:
                # Decode the Base64 encoded data
                decoded_data = base64.b64decode(encoded_data).decode('utf-8')
                print("Decoded Data:", decoded_data)  # For debugging
                
                # Parse the JSON data
                data = json.loads(decoded_data)
                print(data)

                # Extract the relevant fields
                transaction_uuid = data.get('transaction_uuid')
                status = data.get('status')
                total_amount = data.get('total_amount')
                # Add other fields as necessary

                # Update the payment status in the database
                payment = Order.objects.get(transaction_uuid=transaction_uuid)

                redirect=frontend_url+"/track-order/"+str(payment.id)
                print(redirect)
                context={"order_id":payment.id,"redirect_to":redirect}
                if payment:
                    if  status == "COMPLETE":
                        cleaned_amount = total_amount.replace(",", "")
                        payment.payment_status = "completed"
                        payment.paid_amount = Decimal(cleaned_amount)
                        payment.full_clean()  # Validate the payment object
                        payment.save()

                        return render(request,'success.html',context)
                    
                    else:
                        payment.payment_status = "procesing"
                        payment.save()
                        return render(request,'paymenterror.html')

                else:
                    return JsonResponse({'error': 'Transaction not found.'}, status=404)

            except (ValueError, json.JSONDecodeError) as e:
                print(f"Error decoding data: {e}")
                return JsonResponse({'error': 'Invalid data.'}, status=400)
        
        return JsonResponse({'error': 'No data provided.'}, status=400)
    
from django.shortcuts import render
from django.utils.timezone import now
from num2words import num2words

@staticmethod
@api_view(['GET'])
def order_slip_view(request):

    # Fetch the order and related objects
    order_id=request.GET.get("order_id")
    response_type=request.GET.get("response_type")
    order_obj = get_object_or_404(
        Order.objects.prefetch_related('orderitem_set__product','shippingdetails'),
        id=order_id
    )
    
    # Calculate the total amount (you can also use order_obj.paid_amount directly if it's already stored)
    total_amount = order_obj.paid_amount or 0

    # Convert the amount to words in Nepali
    print(total_amount)
    rupees = int(total_amount)
    paisa = int((total_amount - rupees) * 100)

    # Convert to words
    rupees_in_words = num2words(rupees, lang='en') + ' rupees'
    paisa_in_words = num2words(paisa, lang='en') + ' paisa' if paisa > 0 else ''

    amount_in_words = f"{rupees_in_words} and {paisa_in_words}" if paisa > 0 else rupees_in_words
    # amount_in_words = num2words(total_amount, lang='ne') + ' रुपैया'  # Nepali currency format

    # Prepare context with relevant order details
    shipping_details = order_obj.shippingdetails.get(order=order_obj)
    
    context = {
        'order_date': order_obj.created_at,  
        'ordered_by': {
            'name': shipping_details.fullname if shipping_details else '',
            'phone': shipping_details.phonenumber if shipping_details else '',
            'country': shipping_details.country if shipping_details else '',
            'address': f"{shipping_details.city}, {shipping_details.district}" if shipping_details else ''
        },
        'ship_to': {
            'name': shipping_details.fullname if shipping_details else '',
            'phone': shipping_details.phonenumber if shipping_details else '',
            'country': shipping_details.country if shipping_details else '',
            'address': f"{shipping_details.city}, {shipping_details.district}, {shipping_details.land_mark}" if shipping_details else ''
        },
        'order_id': order_obj.orderid,
        'delivery_note': shipping_details.additional_information if shipping_details else '',
        'delivery_date': order_obj.last_modified,
        'delivery_priority': 'Standard',  # Placeholder, customize as needed
        'payment_status': order_obj.payment_status,
        'payment_method': 'Esewa',  # Customize if necessary
        'payment_date': order_obj.last_modified,
        'order_items': [
            {
                'sn': index + 1,
                'particulars': item.product.product_name,
                'quantity': item.quantity,
                'unit_price': item.purchase_amount,
                'amount': item.quantity * item.purchase_amount
            }
            for index, item in enumerate(order_obj.orderitem_set.all())
        ],
        'amount_in_words': amount_in_words
    }
    print(context)
    if response_type=="template":
        return render(request, 'orderslip.html', context)
    
    elif response_type=="json":
        return ResponseMixin.handle_success_response(serialized_data=context,status_code=200,message="order fetched successfully")
    else:
        return ResponseMixin.handle_error_response(error_message="invalid response type",status_code=400)
    

@staticmethod
@api_view(['GET'])
def secretkey(request):
    secret="django-insecure-l0kz3a+3v$ohse*$k-@+)^=wyec91qy-u2ri%&1*+hb^#===(*'"
    return Response({"success":True,"secret_key":secret})



class UploadPaymentProofView(APIView,ResponseMixin):
    def post(self, request, *args, **kwargs):
        serializer = PaymentProofSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.handle_success_response(message="success",status_code=200)
        return self.handle_error_response(error_message=serializer.errors,status_code=400)