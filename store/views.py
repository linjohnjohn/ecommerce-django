from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import *


def store(request):
    items, order, cartItems = cart_details(request)
    products = Product.objects.all()
    context = {'products': products, 'items': items,
               'order': order, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    items, order, cartItems = cart_details(request)

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    items, order, cartItems = cart_details(request)
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    if orderItem.quantity <= 0:
        orderItem.delete()
    else:
        orderItem.save()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    else:
        name = data['form']['name']
        email = data['form']['email']

        items, order, cartItems = cart_details(request)
        customer, created = Customer.objects.get_or_create(
            email=email,
        )
        customer.name = name
        customer.save()

        order = Order.objects.create(
            customer=customer,
            complete=False
        )

        for item in items:
            productId = item['product'].id
            product = Product.objects.filter(pk=productId)
            if product.exists():
                product = product.first()
                orderItem = OrderItem.objects.create(
                    product=product,
                    order=order,
                    quantity=item['quantity']
                )

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete', safe=False)


# helper util function
def cart_details(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cart = json.loads(request.COOKIES.get('cart', "{}"))
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = 0
        for i in cart:
            product = Product.objects.filter(pk=i)
            if product.exists():
                product = product.first()
                quantity = cart[i]['quantity']
                total = product.price * quantity

                order['get_cart_total'] += total
                order['get_cart_items'] += quantity
                cartItems += quantity

                item = {
                    'product': product,
                    'quantity': quantity,
                    'get_total': total
                }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
    return items, order, cartItems
