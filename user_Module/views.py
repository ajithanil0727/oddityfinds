from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from .models import oddityFindsUser,oddityFindsProduct, Category, CartItem, Address, SubImage, Order, OrderItem, Coupon, Offer
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from .helper import create_order, sent_otp, calculate_cart_total
import pyotp
from django.contrib.auth.hashers import check_password
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum




# Create your views here.

# Home view
@never_cache
def home(request):
    if request.user.is_authenticated:   
        user = request.user
        prod = oddityFindsProduct.objects.filter(is_active = True)
        cat = Category.objects.all()
        offer = Offer.objects.filter(products__in = prod) 
        for product in prod:
            product_discounts = [] 
            product_offers = product.offer_set.filter(offer_type='product',is_active=True)
            for offer in product_offers:
                discount = offer.discount
                discounted_price = product.price - discount
                product_discounts.append(discounted_price)

            if product.category:
                category_offers = Offer.objects.filter(categories=product.category, offer_type='category',is_active=True)
                for offer in category_offers:
                    discount = offer.discount
                    discounted_price = product.price - discount
                    product_discounts.append(discounted_price)

            if product_discounts:
                product.dprice = min(product_discounts)
                product.save()

            else:
                product.dprice = 0
                product.save()

        return render(request, 'index.html', {'prod' : prod, 'usr': user, 'cat' : cat, 'offer': offer})
    prod = oddityFindsProduct.objects.all()
    cat = Category.objects.all()
    offer = Offer.objects.filter(products__in = prod)
    for product in prod:
            product_discounts = [] 
            product_offers = product.offer_set.filter(offer_type='product',is_active=True)
            for offer in product_offers:
                discount = offer.discount
                discounted_price = product.price - discount
                product_discounts.append(discounted_price)

            if product.category:
                category_offers = Offer.objects.filter(categories=product.category, offer_type='category',is_active=True)
                for offer in category_offers:
                    discount = offer.discount
                    discounted_price = product.price - discount
                    product_discounts.append(discounted_price)

            if product_discounts:
                product.dprice = min(product_discounts)
                product.save()

            else:
                product.dprice = 0
                product.save()
    return render(request, 'index.html', {'prod' : prod,'cat' : cat, 'offer': offer})

    
# User Login View     
@never_cache
def user_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password'] 
        try:
            user = authenticate(request, email= username, password= password)
            if user is not None and not user.is_staff:
                if user.is_active:
                    # if sent_otp(request):
                        login(request, user)
                        request.session['username'] = username
                        # return redirect('verify_otp')
                        return redirect('home')
                else:
                    messages.error(request, 'Your account is blocked. Contact the administrator for assistance.') 
            else:
                messages.error(request, 'Invalid username or password')

        except oddityFindsUser.DoesNotExist:
            messages.error(request, 'User is not avaliable')

    return render(request, "login.html")

# Otp view
# @never_cache
# def verify_otp(request):
#     if request.method == 'POST':
#         verify_otp = request.POST.get('verify_otp') 

#         if 'username' in request.session:
#             username = request.session['username']
#         else:
#             messages.error(request, 'Username not found in session')
#             return redirect('user_view')

#         otp_secret_key = request.session['otp_secret_key']
#         otp_valid_until = request.session['otp_valid_date']
#         if otp_secret_key and otp_valid_until:
#             valid_until = datetime.fromisoformat(otp_valid_until)
#             if valid_until > datetime.now():
#                 totp = pyotp.TOTP(otp_secret_key, interval = 60)
#                 if totp.verify(verify_otp):
#                     user = get_object_or_404(oddityFindsUser, email = username)
#                     login(request, user)
#                     del request.session['otp_secret_key']
#                     del request.session['otp_valid_date']
#                     return redirect('home')
#                 else:
#                     messages.error(request, 'Invalid one time password')
                    
#             else:
#                 messages.error(request, 'one time password expired')
#         else:
#             messages.error(request, 'something went wrong')


#     return render(request, 'otp.html')

# User signup view
@never_cache
def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phonenum = request.POST['phone']
        if password1 != password2:
            messages.info(request, 'password mismatching')
            return render(request, 'signup.html')
        elif oddityFindsUser.objects.filter(email = email).exists():
            messages.info(request, 'email already exits')
            return render(request, 'signup.html')
        else:
            user = oddityFindsUser.objects.create(first_name = first_name, email = email, last_name = last_name, phone_number = phonenum ) 
            user.set_password(password1)          
            user.save()
            return redirect('user_view')      
    return render(request, 'signup.html')

# Admin Login view
@never_cache
def adminlogin(request):
    if 'username' in request.session:
        return redirect('dashboard')
            
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = authenticate(request, email= username, password= password)
            if user is not None:
                if user.is_staff:
                    request.session['username'] = username
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.info(request, 'login using user login')
                    return redirect('user_view')
        except oddityFindsUser.DoesNotExist:
            messages.info(request, 'invalid credintial')
            return redirect('adminlogin')
    
    return render(request, 'adminlogin.html')


# Admin's User Management view
@login_required(login_url='adminlogin')
def usermanage(request):
    if 'username' in request.session:
        username = request.session['username']
        user = oddityFindsUser.objects.get(email = username)
        if user.is_staff:
            search = request.POST.get('search')
            if search:
                userinfo =oddityFindsUser.objects.filter(email__startswith = search)
            else:
                userinfo = oddityFindsUser.objects.filter(is_staff = False)
            return render(request, 'usermanage.html', {'datas' : userinfo})

# Admin's Product Management view
@login_required(login_url='adminlogin')
def productmanage(request):
    if 'username' in request.session:
        username = request.session['username']
        user = oddityFindsUser.objects.get(email = username)
        prodinfo = oddityFindsProduct.objects.all()
        if user.is_staff:
            search = request.POST.get('search')
            if search:
                prodinfo =oddityFindsProduct.objects.filter(proname__startswith = search)
            else:
                prodinfo = oddityFindsProduct.objects.all()
            return render(request, 'productmanage.html', {'pdata' : prodinfo })

# Admin's Order Management view        
@login_required(login_url='adminlogin')
def ordermanage(request):
    order_items = OrderItem.objects.all()
    user = request.user
    if user.is_staff:
        search = request.POST.get('search')
        if search:
            order_items = OrderItem.objects.filter(product__proname__startswith = search)
        else:
            order_items = OrderItem.objects.all()
    return render(request, 'ordermanage.html',{ 'order': order_items } )


# Admin's Add User view
# @login_required(login_url='adminlogin')  
# def adduser(request): 
#      if request.method == 'POST':
#         first_name = request.POST['first_name']
#         last_name = request.POST['last_name']
#         username = request.POST['username']
#         email = request.POST['email']
#         password1 = request.POST['password1']
#         password2 = request.POST['password2']
#         if password1 != password2:
#             messages.info(request, 'password mismatching')
#             return render(request, 'adduser.html')
#         elif oddityFindsUser.objects.filter(username = username).exists():
#             messages.info(request, 'username not avaliable')
#             return render(request, 'adduser.html')
#         elif oddityFindsUser.objects.filter(email = email).exists():
#             messages.info(request, 'email already exists')
#             return render(request, 'adduser.html')
#         else:
#             user = oddityFindsUser(first_name = first_name, last_name = last_name, username = username, password = password1, email = email)
#             user.save()
#             return redirect('dashboard')      
#      return render(request, 'adduser.html')

# Admin's Edit User view
@login_required(login_url='user_view')
def edituser(request,id):
    user = oddityFindsUser.objects.get(id = id)
    if request.method == 'POST':
        user.first_name = request.POST.get('firstname')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone')
        user.save()
        target_url = reverse('userprofile', kwargs={'id': id })
        return redirect(target_url)
    return render(request, 'edit_user.html', {'user': user})

# Admin's Delete User view
@login_required(login_url='adminlogin') 
def deleteuser(request,id):
    user = oddityFindsUser.objects.get(id =id)
    if user.is_active:
        user.is_active = False
        user.save()
    else:
        user.is_active = not user.is_active
        user.save()
    return redirect('usermanage')

# Admin's Delete Product view
@login_required(login_url='adminlogin') 
def deleteproduct(request, id):
    product = oddityFindsProduct.objects.get(id = id)
    if product.is_active:
        product.is_active = False
        product.save()
    else:
        product.is_active = not product.is_active
        product.save()
    return redirect('productmanage')

# Admin's Delete Category view
@login_required(login_url='adminlogin') 
def deletecategory(request, id):
    category = Category.objects.get(id = id)
    if category.is_active:
        category.is_active = False
        category.save()
    else:
        category.is_active = not category.is_active
        category.save()
    return redirect('categorymanage')


# Admin's Delete Address view
@login_required(login_url='user_view') 
def deleteaddress(request,id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    return redirect('viewaddress')

# Admin's Add Product view
@login_required(login_url='adminlogin') 
def addproduct(request):
    if request.method == 'POST':
       pname = request.POST['pname']
       description = request.POST['descr']
       category = Category.objects.get(categoryname = request.POST['category'])
       image = request.FILES['image']
       variant_prices = request.POST.get('variant_price_list')
       variant_quantitys = request.POST.get('variant_quantity_list')
       if oddityFindsProduct.objects.filter(proname = pname).exists():
           messages.info(request, 'name not avaliable')
           return render(request, 'addproduct.html')
       else:
            product = oddityFindsProduct.objects.create(proname = pname, description = description,  category= category, price=variant_prices, quantity=variant_quantitys, main_image = image)
            product.save()
            for file in request.FILES.getlist('subimages'):
                SubImage.objects.create(product=product, image=file)
            return redirect('dashboard')  
    cat = Category.objects.all()
    return render(request, 'addproduct.html', {'cat': cat})

# Admin's Add Offer view
@login_required(login_url='adminlogin') 
def addoffer(request):
    prod = oddityFindsProduct.objects.all()
    cat = Category.objects.all()
    print(prod)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        offer_type = request.POST.get('offer_type')
        discount = request.POST.get('discount')
        product_ids = request.POST.get('products', '').split(',')
        category_ids = request.POST.get('categories', '').split(',')
        if offer_type == 'product':
            product_ids = request.POST.get('products', '').split(',')
            products = oddityFindsProduct.objects.filter(id__in=product_ids)
            categories = []

        elif offer_type == 'category':
            category_ids = request.POST.get('categories', '').split(',')
            categories = Category.objects.filter(id__in=category_ids)
            products = []

        else:
            products = []
            categories = []
            return redirect('dashboard') 
        offer = Offer.objects.create(title=title,description=description,offer_type=offer_type,discount=discount) 
        offer.products.set(products)
        offer.categories.set(categories)
        offer.save()
        return redirect('offermanage')
    return render(request, 'addoffer.html', {'cat': cat, 'prod': prod})

# Admin's Offer Management view
@login_required(login_url='adminlogin')
def offermanage(request):
    user = request.user
    offer = Offer.objects.all()
    if user.is_staff:
        search = request.POST.get('search')
        if search:
            offer = Offer.objects.filter(title__startswith = search)
        else:
            offer = Offer.objects.all()
    return render(request, 'offermanage.html', {'offer': offer})

# Admin's Delete Offer view    
@login_required(login_url='adminlogin')
def deleteoffer(request,id):
    offer = Offer.objects.get(id = id)
    if offer.is_active:
        offer.is_active = False
        offer.save()
    else:
        offer.is_active = not offer.is_active
        offer.save()
    return redirect('offermanage')
    


# Admin's Edit Product view
@login_required(login_url='adminlogin') 
def editproduct(request,id):
    product = get_object_or_404(oddityFindsProduct, id= id)
    print(product.proname)
    if request.method == 'POST':
       product.proname= request.POST['pname']
       product.description = request.POST['descr']
       product.category = Category.objects.get(categoryname = request.POST['category'])
    #    product.main_image = request.FILES['image']
       product.variant_type = request.POST.get('variant_type_list')
       product.variant_name = request.POST.get('variant_name_list')
       product.price = request.POST.get('variant_price_list')
       product.quantity = request.POST.get('variant_quantity_list')
       if oddityFindsProduct.objects.exclude(id=id).filter(proname=product.proname).exists():
           messages.info(request, 'name not avaliable')
           return render(request, 'addproduct.html')
       else:
            product.save()
            # product.subimage_set.all().delete()
            # for file in request.FILES.getlist('subimages'):
            #     SubImage.objects.create(product=product, image=file)
            return redirect('dashboard')  
    cat = Category.objects.all()
    return render(request, 'editproduct.html', {'cat': cat, 'product': product})

#Userside Product Detail view
def singleproduct(request,id):
    prod = oddityFindsProduct.objects.get(id= id)
    subimg = SubImage.objects.filter(product_id = id)
    return render(request, 'single-product.html', {'prod' : prod, 'subimg' : subimg })

# Admin's Add Category view
@login_required(login_url='adminlogin') 
def addcategory(request):
    if request.method == 'POST':
        catname = request.POST['catname']
        description = request.POST['desc']
        if Category.objects.filter(categoryname = catname).exists():
                messages.info(request, 'name not avaliable')
                return redirect(request, 'addcategory')
        else:
            cate = Category(categoryname = catname, description = description)
            cate.save()
            return redirect('addproduct')
    return render(request, 'addcategory.html') 

# Admin's Edit Category view
@login_required(login_url='adminlogin')
def editcategory(request,id):
    category = get_object_or_404(Category, pk= id)
    if request.method == 'POST':
        category.categoryname = request.POST['catname']
        category.description = request.POST['desc']
        if Category.objects.exclude(id=id).filter(categoryname = category.categoryname).exists():
                messages.info(request, 'name not avaliable')
                return redirect('editcategory')
        else:
            category.save()
            return redirect('dashboard')
    return render(request, 'editcategory.html', {'cat': category}) 

# Admin's Dashboard view
@login_required(login_url='adminlogin')
def dashboard(request):
    orderitem = OrderItem.objects.all().order_by('-order__order_date')
    totalpro = OrderItem.objects.aggregate(ptotal = Sum('quantity'))
    totalamt = OrderItem.objects.aggregate(amttotal = Sum('item_price'))
    user = oddityFindsUser.objects.all().count()
    prod = oddityFindsProduct.objects.all().count()
    return render(request, 'dashboard.html', {'user': user,'prod': prod, 'order': orderitem, 'topro': totalpro['ptotal'], 'amt':totalamt['amttotal'], })

# Admin's ategory Management view
@login_required(login_url='adminlogin') 
def categorymanage(request):
    if 'username' in request.session:
        username = request.session['username']
        user = oddityFindsUser.objects.get(email = username)
        cateinfo = Category.objects.all()
        if user.is_staff:
            search = request.POST.get('search')
            if search:
                cateinfo =Category.objects.filter(categoryname__startswith = search)
            else:
                cateinfo = Category.objects.all()
            return render(request, 'categorymanage.html', {'cdata' : cateinfo })

# Admin's Stock Management View
@login_required(login_url='adminlogin')
def stockmanage(request):
    user = request.user
    products = oddityFindsProduct.objects.all()
    if user.is_staff:
        search = request.POST.get('search')
        if search:
            products = oddityFindsProduct.objects.filter(proname__startswith = search)
        else:
            cateinfo = Category.objects.all()
        return render(request, 'stockmanage.html', {'products': products})

#User Profile View
@login_required(login_url='user_view') 
def userprofile(request,id):
    return render(request, 'userprofile.html')

#Filter By Category View
def filterby(request,id):
    if request.user.is_authenticated: 
        user = request.user
        category_obj = Category.objects.get(id = id)
        prod = oddityFindsProduct.objects.filter(category = category_obj)
        cat = Category.objects.all()
        # product_list = [{'proname': product.proname, 'description': product.description, 'price': product.price} for product in prod]
        # return JsonResponse({'products': product_list, 'success':True})
        return render(request, 'category.html', {'prod' : prod, 'usr' : user, 'cat' : cat})

#Userside Add To Cart View
@login_required(login_url='user_view') 
def addtocart(request,id):
    product = oddityFindsProduct.objects.get(id =  id)
    user = request.user
    cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('home')

#Userside Products OrderDetails View
@login_required(login_url='user_view')
def vieworderitem(request,id):
    orderitem = get_object_or_404(OrderItem, id= id)
    return render(request, 'vieworderitem.html', {'item': orderitem})

#User's Cart View
@login_required(login_url='user_view')
@transaction.atomic
def cart(request):
    user = request.user
    cus = oddityFindsUser.objects.get(email = user)
    cart_items = CartItem.objects.filter(user=cus)
    items_num = CartItem.objects.filter(user=cus).count()
    addre = Address.objects.filter(user = cus)
    total = calculate_cart_total(cart_items)
    if request.method == 'POST': 
        selectedadd = request.POST.get('selected_address')
        address = Address.objects.get(id = selectedadd)
        print(selectedadd)
        payment_option = request.POST['payment_option']
        coup = request.POST['coupon']
        try:
            cop = Coupon.objects.get(code= coup)
            if cop.active:
                discount = cop.discount 
                total -= discount
        except Coupon.DoesNotExist:
            pass
        if payment_option == 'wallet':
            if cus.wallet >= total:
                cus.wallet = user.wallet - total
                cus.save()
            else:
                messages.error(request, 'not enough balance in wallet')
                return redirect('cart')
        elif payment_option == 'upi':
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            amount = int(total*100)
            payment = client.order.create({'amount': amount, 'currency': 'INR','payment_capture': '1'})
            order = create_order(cus, cart_items, total, payment_option, address)
            if order:
                cart_items.delete()
                ordered_items = OrderItem.objects.filter(order=order)
                for ordered_item in ordered_items:
                    product = ordered_item.product
                    quantity_ordered = ordered_item.quantity
                    product.quantity -= quantity_ordered
                    product.save()
                messages.success(request, 'Order placed successfully!')
                return render(request, 'paymentpage.html', {'user':cus, 'payment':payment, 'order':order})
        else:
            pass
        order = create_order(cus, cart_items, total, payment_option, address)   
        if order:
            cart_items.delete()
            ordered_items = OrderItem.objects.filter(order=order)
            for ordered_item in ordered_items:
                product = ordered_item.product
                quantity_ordered = ordered_item.quantity
                product.quantity -= quantity_ordered
                product.save()
            messages.success(request, 'Order placed successfully!')
            return redirect('ordersucess', id = order.id)  
        else:
            messages.error(request, 'Failed to create the order. Please try again.')
    return render(request, 'cart.html', {'cart_items': cart_items, 'addre': addre, 'num' : items_num, 'total': total})

#Userside Order Detail View
@login_required(login_url='user_view')
def myorder(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    order_items = OrderItem.objects.filter(order__in=orders).order_by('-order__order_date')
    orders_per_page = 4
    paginator = Paginator(order_items, orders_per_page)
    page = request.GET.get('page')
    try:
        order_items = paginator.page(page)
    except PageNotAnInteger:
        
        order_items = paginator.page(1)
    except EmptyPage:
       
        order_items = paginator.page(paginator.num_pages)
    return render(request, 'myorder.html' ,{'orders': orders, 'order_items': order_items})

#Userside Cancel Order View
@login_required(login_url='user_view')
def cancelorder(request,id):
    order = get_object_or_404(OrderItem, id=id)
    user = request.user
    cus = oddityFindsUser.objects.get(email = user)
    if order.is_paid:
        total_amount = order.item_price
        cus.wallet += total_amount
        cus.save()
        order.is_cancel = True
        order.item_price = 0
        order.status = 'Cancelled'
        order.save()
        product = order.product
        product.quantity += order.quantity
        product.save()
        messages.success(request, 'Order cancelled!')
        return redirect('myorder')
    else:
        order.is_cancel = True
        order.status = 'Cancelled'
        order.save()
        product = order.product
        product.quantity += order.quantity
        product.save()
        return redirect('myorder')


#Userside Remove Product From Cart View
@login_required(login_url='user_view')  
def removefromcart(request,id):
    if not request.user.is_authenticated:
        return redirect('user_view')
    item = get_object_or_404(CartItem, id=id, user=request.user)
    item.delete()
    return redirect('cart')

#Usersied Add Address View
@login_required(login_url='user_view')  
def addaddress(request):
    if request.method == 'POST':
        address_line1 = request.POST['address_line1']
        address_line2 = request.POST['address_line2']
        city = request.POST['city']
        state = request.POST['state']
        postal_code = request.POST['postal_code']
        country = request.POST['country']
        new_address = Address(user=request.user, address_line1=address_line1, address_line2=address_line2, city=city, state=state, postal_code=postal_code, country=country)
        new_address.save()
        user_id = request.user.id
        url = reverse('userprofile', kwargs={'id': user_id})
        return redirect(url)
    return render(request, 'addaddress.html')

#Userside View Address View
@login_required(login_url='user_view') 
def viewaddress(request):
    user_addresses = Address.objects.filter(user=request.user)
    return render(request, 'viewaddress.html', {'addresses': user_addresses})

#Userside Edit Address View
@login_required(login_url='user_view') 
def editaddress(request,id):
    address = get_object_or_404(Address, id=id, user=request.user)
    if request.method == 'POST':
        address.address_line1 = request.POST.get('address_line1', address.address_line1)
        address.address_line2 = request.POST.get('address_line2', address.address_line2)
        address.city = request.POST.get('city', address.city)
        address.state = request.POST.get('state', address.state)
        address.postal_code = request.POST.get('postal_code', address.postal_code)
        address.country = request.POST.get('country', address.country)
        address.save()
        return redirect('viewaddress')  
    return render(request, 'editaddress.html', {'address': address})

#Userside Buy Now View
@login_required(login_url='user_view') 
def buy(request,id):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    prod = oddityFindsProduct.objects.get(id = id)
    addre = Address.objects.filter(user= user)
    total = calculate_cart_total(cart_items)
    try:
        cart_item = CartItem.objects.get(user=user, product=prod)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(user=user, product=prod, quantity=1)   
    return redirect('cart')

#Userside Minimum Sort View 
def minsortview(request):
    if request.user.is_authenticated: 
        user = request.user
        prod = oddityFindsProduct.objects.all().order_by('price')
        return render(request, 'category.html', {'prod' : prod, 'usr': user})

#Userside Maximum Sort View    
def maxsortview(request):
    if request.user.is_authenticated: 
        user = request.user
        prod = oddityFindsProduct.objects.all().order_by('-price')
        return render(request, 'category.html', {'usr': user, 'prod': prod})

#Userside Product Quantity Increase View
@login_required(login_url='user_view') 
def addquantity(request,id):
    if request.method == 'POST':
        user = request.user
        product = oddityFindsProduct.objects.get(id = id)
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        max_qua = product.quantity
        if not created:
            if cart_item.quantity < max_qua:
                cart_item.quantity += 1
                cart_item.save()
            else :
                cart_item.quantity = max_qua
                cart_item.save()
                messages.error(request, 'quantity limit reached')    
            return redirect('cart')
        

#Userside Product Quantity Decrease View
@login_required(login_url='user_view') 
def minusquantity(request,id):
    if request.method == 'POST':
        user = request.user
        product = oddityFindsProduct.objects.get(id = id)
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        return redirect('cart')
        

#Userside Order Sucess Page View
@login_required(login_url='user_view') 
@csrf_exempt
def ordersucess(request,id):
    user = request.user
    orders = get_object_or_404(Order, id=id)
    order_items = OrderItem.objects.filter(order=orders)
    current_time = datetime.now()
    return render(request, 'ordersucess.html', {'order' : orders, 'items': order_items, 'user' : user, 'time':current_time })

#Userside Change Password View
@login_required(login_url='user_view')
def changepassword(request,id):
    user = oddityFindsUser.objects.get(id=id)
    if request.method == 'POST':
        current_password = request.POST['old']
        new_password = request.POST['new']
        confirm_new_password = request.POST['new1']
        if check_password(current_password, user.password):
            if user is not None:
                if new_password == confirm_new_password:
                    user.set_password(new_password)
                    user.save()
                    messages.error(request, 'password changed sucessfully')
                    return redirect('user_view')
                else:
                    messages.error(request, 'password mismaching')
        else:
             messages.error(request, 'current password mismaching')
    return render(request, 'changepassword.html',{'user' :user })

#Admin's Delivery button View
@login_required(login_url='adminlogin')
def mark_order_delivered(request, id):
    order = get_object_or_404(OrderItem, id= id)
    if order.status != 'Delivered':
        order.status = 'Delivered'
        order.save()
    return redirect('ordermanage')
    
#Userside Order Return view
@login_required(login_url='user_view')     
def returnorder(request, id):
    order = get_object_or_404(OrderItem, id=id)
    user = request.user
    cus = oddityFindsUser.objects.get(email = user)
    if order.status == 'Delivered' and not order.returned:
        if order.is_paid:
            total_amount = order.item_price
            cus.wallet += total_amount
            cus.save()
            order.item_price = 0
            order.returned = True
            order.status = 'returned'            
            order.save()
            product = order.product
            product.quantity += order.quantity
            product.save()
            return redirect('myorder')
        else:
            order.returned = True
            order.status = 'returned'            
            order.save()
            product = order.product
            product.quantity += order.quantity
            product.save()
            return redirect('myorder')
    return redirect('myorder')

#Admin's Add Coupon view
@login_required(login_url='adminlogin')   
def addcoupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount = request.POST.get('discount')
        if Coupon.objects.filter(code = coupon_code).exists():
            messages.info(request, 'code not avaliable')
            return redirect('addcoupon')
        else:
            coupon = Coupon.objects.create(code=coupon_code, discount=discount)
            coupon.save()
            return redirect('couponmanage')
    return render(request, 'addcoupon.html')

#Admin's Coupon Management View
@login_required(login_url='adminlogin')
def couponmanage(request):
    coupon = Coupon.objects.all()
    user = request.user
    if user.is_staff:
        search = request.POST.get('search')
        if search:
            coupon = Coupon.objects.filter(code__startswith = search)
        else:
            coupon = Coupon.objects.all()
    return render(request, 'couponmanage.html',{ 'coupon': coupon } )


#Admin's Delete Coupon View   
@login_required(login_url='adminlogin')
def deletecoupon(request,id):
    coupon = Coupon.objects.get(id =id)
    if coupon.active:
        coupon.active = False
        coupon.save()
    else:
        coupon.active = not coupon.active
        coupon.save()
    return redirect('couponmanage')

#Userside View Coupon View   
@login_required(login_url='user_view')
def coupons(request):
    coup = Coupon.objects.filter(active = True)
    return render(request, 'coupon.html', {'coupon': coup})

#Userside Wallet View
@login_required(login_url='user_view')
def wallet(request):
    user = request.user
    userd = oddityFindsUser.objects.get(email = user)
    return render(request, 'wallet.html' ,{'user': userd})

#Admin's Ordered Product Detail View
@login_required(login_url='adminlogin')
def adminorderitemdetail(request, id):
    orderitem = get_object_or_404(OrderItem, id= id)
    return render(request, 'orderitemdetails.html', {'item': orderitem})

#Admin's Edit Offer View
@login_required(login_url='adminlogin') 
def editoffer(request,id):
    offer = get_object_or_404(Offer, id=id)
    if request.method == 'POST':
        offer.title = request.POST.get('title', offer.title)
        offer.discount = request.POST.get('discount', offer.discount)
        offer.save()
        return redirect('offermanage')  
    return render(request, 'editoffer.html', {'offer': offer})