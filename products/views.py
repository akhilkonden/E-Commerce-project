from django.shortcuts import render,redirect
from django.http import JsonResponse , HttpResponseRedirect
from django.contrib.auth.models import User , auth
from django.contrib import messages
from django.urls import reverse
import json
import datetime
from .models import *


# Create your views here.

def index(request):
    return render(request,"index.html")

def store(request):
    
    if request.user.is_authenticated:
          customer = request.user.customer
          order , created = Order.objects.get_or_create(customer=customer , complete =False)
          items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0 , 'get_cart_items': 0, 'shipping':False} 
        cartItems = order["get_cart_items"]

    products = Product.objects.all()
    context = {'products': products}
    return render(request,"store.html",context)

def cart(request):
     
     if request.user.is_authenticated:
          customer = request.user.customer
          order , created = Order.objects.get_or_create(customer=customer , complete =False)
          items = order.orderitem_set.all()
     else:
        items = []
        order = {'get_cart_total':0 , 'get_cart_items': 0 , 'shipping':False}
     context = {'items':items, 'order' :order}
     return render(request, "cart.html", context)

def checkout(request):
     if request.user.is_authenticated:
          customer = request.user.customer
          order , created = Order.objects.get_or_create(customer=customer , complete =False)
          items = order.orderitem_set.all()
     else:
        items = []
        order = {'get_cart_total':0 , 'get_cart_items': 0 , 'shipping':False}
     context = {'items':items, 'order' :order}
     
     return render(request, 'checkout.html', context)

def contact(request):
     if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        # Save message to database
        Contact.objects.create(name=name, email=email,subject=subject, message=message)

        # Redirect to thank you page
        messages.success(request, "Thanks For your Message")
     return render(request, 'contact.html')
     

def updateItem(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']

     print('Action:', action)
     print('productId:', productId)

     customer = request.user.customer
     product = Product.objects.get(id=productId)
     order , created = Order.objects.get_or_create(customer=customer , complete=False)

     orderItem , created = OrderItem.objects.get_or_create(order=order,product=product)

     if action == 'add':
          orderItem.quantity = (orderItem.quantity + 1)
     elif action == 'remove':
          orderItem.quantity = (orderItem.quantity - 1)

     orderItem.save()

     if orderItem.quantity <= 0:
          orderItem.delete()

     return JsonResponse('Item was added' , safe=False)

def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          customer = request.user.customer
          order , created = Order.objects.get_or_create(customer=customer , complete=False)
          total = float(data['form']['total'])
          order.transaction_id = transaction_id

          if total == order.get_cart_total:
               order.complete = True
          order.save()

          if order.shipping == True:
               ShippingAddress.objects.create(
                    customer = customer,
                    order = order,
                    address = data['shipping']['address'],
                    city = data['shipping']['city'],
                    state = data['shipping']['state'],
                    zipcode = data['shipping']['zipcode'],
               )

     else:
          print('user is not logged in...')
     return JsonResponse('payment complete!', safe=False)
