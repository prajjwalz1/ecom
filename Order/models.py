from django.db import models
from product.mixins import *
from product.models import Product,ProductVariant,VariantColors
# Create your models here.

class OrderItem(CustomizedModel):
    order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,related_name='orderitems'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product_variant=models.ForeignKey(ProductVariant,on_delete=models.SET_NULL,null=True,blank=True)
    product_color=models.CharField(max_length=255,null=True,blank=True,editable=False)
    quantity=models.IntegerField(null=True,blank=True,default=1)
    purchase_amount=models.DecimalField(decimal_places=2,max_digits=8)

    def __str__(self):
        return f"{self.product.product_name}"


class ShippingDetails(CustomizedModel):
    order=models.OneToOneField('Order',on_delete=models.DO_NOTHING,related_name='shippingdetails')
    country=models.CharField(max_length=255,null=False,blank=False)
    fullname=models.CharField(max_length=255,null=False,blank=False)
    district=models.CharField(max_length=255,null=False,blank=False)
    city=models.CharField(max_length=255,null=False,blank=False)
    phonenumber=models.CharField(max_length=255,null=False,blank=False)
    alternate_phone_numbers=models.CharField(max_length=255,null=False,blank=True)
    land_mark=models.CharField(max_length=255,null=False,blank=False)
    postal_code=models.CharField(max_length=255,null=False,blank=False)
    additional_information=models.CharField(max_length=255,null=True,blank=True)
    email=models.EmailField(null=False,blank=False)
    request_delivery_date=models.DateField(null=True,blank=True)


class PromoCode(CustomizedModel):
    """
    Model to represent a promotional coupon code with either a flat amount or percentage discount.
    """
    
    DISCOUNT_TYPE_FLAT = 'FLAT'
    DISCOUNT_TYPE_PERCENTAGE = 'PERCENTAGE'
    
    DISCOUNT_TYPE_CHOICES = [
        (DISCOUNT_TYPE_FLAT, 'Flat Amount'),
        (DISCOUNT_TYPE_PERCENTAGE, 'Percentage'),
    ]

    code = models.CharField(max_length=20, unique=True, help_text="Unique code for the promo.")
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default=DISCOUNT_TYPE_FLAT,
        help_text="Type of discount: flat amount or percentage."
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Discount amount when using flat amount else make it 0.",
        default=0
    )
    # dicount_currency=models.CharField(max_length=255,choices=("$","NRs"))
    discount_percentage = models.FloatField(
     
        help_text="Discount in percentage only applicable when using Discount Type 'PERCENTAGE' else make it zero",default=0
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Maximum discount amount applicable when using percentage discount.",
        default=0
    )
    start_date = models.DateTimeField(default=timezone.now, help_text="Start date for the promo code.")
    end_date = models.DateTimeField(default=timezone.now, help_text="End date for the promo code.")
    is_active = models.BooleanField(default=True, help_text="Is the promo code currently active?")
    count=models.IntegerField(default=0,editable=False)
    limit_users=models.BooleanField(default=False, help_text="Is the promo code limited in number?")
    max_users=models.IntegerField(default=0)

    def __str__(self):
        return self.code
    def is_valid(self):
        """
        Check if the promo code is valid based on the current date and status.
        """
        now = timezone.now()
        return self.is_active and (self.start_date <= now) and (self.end_date is None or self.end_date >= now)
    
class Order(CustomizedModel):
    qr_payment_slip=models.ForeignKey("PaymentProof", on_delete=models.SET_NULL,null=True,blank=True)
    orderid=models.CharField(max_length=255,null=True,blank=True)
    order_status=models.CharField(choices=(('order_created','New order'),('order_viewed','Order viewed'),('next_delivery','Ready to deliver'),('shipped','shipped'),('product_received','product_received')),default='order_created')
    transaction_uuid=models.CharField(max_length=255,null=True,blank=True)
    cart_amount=models.DecimalField(decimal_places=2,max_digits=8)
    promotional_discount=models.DecimalField(decimal_places=2,max_digits=8)
    promocode_applied=models.BooleanField(default=False)
    promocode_used=models.ForeignKey(PromoCode,null=True,blank=True,on_delete=models.DO_NOTHING)
    price_after_discount=models.DecimalField(decimal_places=2,max_digits=8)
    paid_amount=models.DecimalField(decimal_places=2,max_digits=8,null=True)
    payment_status=models.CharField(choices=(("pending","pending"),("processing","procesing"),("completed","completed")),default=None,null=True,blank=True)
    def __str__(self):
        return self.orderid
    

class PaymentProof(CustomizedModel):
    image = models.ImageField(upload_to="paymentscreenshots")
    payment_note = models.CharField(max_length=255, blank=True, null=False)

    def __str__(self):
       try:
            order = Order.objects.filter(qr_payment_slip__id=self.id).order_by('-created_at').first()
            return order.shippingdetails.phonenumber if order.shippingdetails else "None"
       except Exception as e:
           return "None"
    
       