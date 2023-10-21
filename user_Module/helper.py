import pyotp
from twilio.rest import Client
from django.contrib import messages
from datetime import datetime, timedelta

from user_Module.models import Order, OrderItem


def sent_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=1)
    request.session['otp_valid_date'] = str(valid_date)
    account_sid = 'ACec651c3edcf1755dd97e51b6ae9ad0e2'
    auth_token = '6e5d09e8c44d27a0aad88580711a306a'
    client = Client(account_sid, auth_token)
    from_number = '+12563049602'
    to_number = '+918089972542'
    try:
        message = client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=from_number,
            to=to_number
        )
        print(message)
        print('OTP sent successfully')
        return True
    except Exception as e:
        print(f'Error sending OTP: {str(e)}')
        messages.error(request, 'Error sending OTP')
        return False 




def calculate_cart_total(cart_items):
    total_price = 0
    for cart_item in cart_items:
        product = cart_item.product
        quantity = cart_item.quantity
        if product.dprice > 0:
            price = product.dprice
            item_total = price * quantity
        else:
            price = product.price  
            item_total = price * quantity
            print(item_total)
        total_price += item_total
    return total_price


def create_order(cus, cart_items, total_price, payment_option, address):
    print(payment_option)
    try:
        order = Order.objects.create(user=cus, total_price=total_price, payment_option=payment_option, address = address)
        for item in cart_items:
            if item.product.dprice > 0:
                item_price = item.product.dprice * item.quantity       
            else:
                item_price = item.product.price * item.quantity
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, item_price=item_price)
        order_item = OrderItem.objects.filter(order=order)
        if payment_option in ['upi', 'wallet']:
            for item in order_item:
                item.is_paid = True
                item.save()

                
        return order
    except Exception as e:
        print("Error creating order:", str(e))
        return None


