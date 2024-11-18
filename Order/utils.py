from rest_framework import status
from rest_framework.response import Response
from .models import PromoCode, Order

def apply_promo_code_to_order(order_id, promo_code):
    """
    Applies a promo code to an order and returns the updated order.
    
    Args:
        order_id (str): The order ID to which the promo code should be applied.
        promo_code (str): The promo code to apply.
    
    Returns:
        dict: A response-like dictionary with a status and message or error.
    """
    try:
        order = Order.objects.get(orderid=order_id)
    except Order.DoesNotExist:
        return {"success": False, "status": status.HTTP_404_NOT_FOUND}
    
    try:
        print(promo_code)
        promo = PromoCode.objects.get(code=promo_code)
        
    except PromoCode.DoesNotExist:
        return {"success": False, "status": status.HTTP_400_BAD_REQUEST}
    
    # Check if promo code is valid
    if not promo.is_valid():
        return {"success": False,"error": "Promo code is not valid or has expired.", "status": status.HTTP_400_BAD_REQUEST}

    # Check if the promo code has already been used (if limited per user)
    if promo.limit_users and promo.count >= promo.max_users:
        return {"success": False,"error": "Promo code usage limit reached.", "status": status.HTTP_400_BAD_REQUEST}
    
    # Calculate the discount
    if promo.discount_type == PromoCode.DISCOUNT_TYPE_FLAT:
        # Apply flat discount
        discount = promo.discount_amount
        if promo.discount_amount > order.cart_amount:
            discount = order.cart_amount  # Ensure it doesn't exceed the cart amount
    elif promo.discount_type == PromoCode.DISCOUNT_TYPE_PERCENTAGE:
        # Apply percentage discount
        discount = (promo.discount_percentage / 100) * float(order.cart_amount)
        if promo.max_discount_amount and discount > promo.max_discount_amount:
            discount = promo.max_discount_amount  # Limit to max discount if applicable

    # Update the order with the promo code details
    order.promocode_used = promo
    order.promotional_discount = discount
    order.price_after_discount = order.cart_amount - discount
    order.promocode_applied = True
    
    # Update the promo code count
    if promo.limit_users:
        promo.count += 1
        promo.save()

    # Save the updated order
    order.save()
    # print(discount)
    # return discount
    return {
        "success": True,
        "message": "Promo code applied successfully.",
        "order_id": order.orderid,
        "cart_amount": str(order.cart_amount),
        "promotional_discount": str(order.promotional_discount),
        "price_after_discount": str(order.price_after_discount),
        "promo_code": promo.code,
        "promo_discount_type": promo.discount_type,
        "discount_applicable":discount,
        "promo_discount_percentage": str(promo.discount_percentage),
    }
