from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ShoeCategory, Product, ShoeSize, ProductImage, GENDER_CHOICES, SHOE_TYPE_CHOICES, Cart, CartItem, Order, OrderItem
import json
from decimal import Decimal

def index(request):
    featured_products = Product.objects.filter(available=True)[:20]
    return render(request, 'store/index.html', {'featured_products': featured_products})

def product_list(request, category_slug=None):
    category = None
    categories = ShoeCategory.objects.all()
    products = Product.objects.filter(available=True)
    
    # Get filter parameters
    gender = request.GET.get('gender', None)
    shoe_type = request.GET.get('shoe_type', None)
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    size = request.GET.get('size', None)

    # Apply category filter
    if category_slug:
        category = get_object_or_404(ShoeCategory, slug=category_slug)
        products = products.filter(category=category)
    
    # Apply gender filter
    if gender:
        products = products.filter(gender=gender)
    
    # Apply shoe type filter
    if shoe_type:
        products = products.filter(shoe_type=shoe_type)
    
    # Apply price range filter
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Apply size filter
    if size:
        products = products.filter(sizes__size=size)
     # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'gender_choices': GENDER_CHOICES,
        'shoe_type_choices': SHOE_TYPE_CHOICES,
        'current_gender': gender,
        'current_shoe_type': shoe_type,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_size': size,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    sizes = product.sizes.all().order_by('size')
    related_products = Product.objects.filter(category=product.category, available=True).exclude(id=id)[:4]
    product_images = product.images.all().order_by('order')
    
    # If no image exists, use default image from product itself
    if not product_images.exists():
        main_image = product.image
    else:
        # Get main image or first image in order
        main_image = product_images.filter(is_main=True).first()
        if not main_image:
            main_image = product_images.first()
            if main_image:
                main_image = main_image.image
            else:
                main_image = product.image
        else:
            main_image = main_image.image
    
    context = {
        'product': product,
        'sizes': sizes,
        'related_products': related_products,
        'product_images': product_images,
        'main_image': main_image,
    }
    return render(request, 'store/product_detail.html', context)

def search_products(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).filter(available=True)
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'store/product_list.html', context)


def get_cart(request):
    """Get or create a cart based on user authentication or session cart_id"""
    # If user is authenticated, try to get their cart
    if request.user.is_authenticated:
        user_carts = Cart.objects.filter(user=request.user)
        if user_carts.exists():
            cart = user_carts.first()
            # Store cart ID in session for consistency
            request.session['cart_id'] = str(cart.id)
            return cart
    
    # Fall back to session-based cart if no user cart exists
    cart_id = request.session.get('cart_id')
    try:
        cart = Cart.objects.get(id=cart_id)
        # If user is authenticated but cart has no user assigned, assign it
        if request.user.is_authenticated and not cart.user:
            cart.user = request.user
            cart.save()
    except (Cart.DoesNotExist, TypeError):
        cart = Cart.objects.create(user=request.user if request.user.is_authenticated else None)
        request.session['cart_id'] = str(cart.id)
    
    return cart


@require_POST
def cart_add(request):
    """Add a product to the cart"""
    data = json.loads(request.body)
    product_id = data.get('product_id')
    size_value = data.get('size')
    quantity = int(data.get('quantity', 1))
    
    # Validate data
    if not product_id or not size_value:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    try:
        product = Product.objects.get(id=product_id, available=True)
        size = ShoeSize.objects.get(product=product, size=size_value)
        
        # Check stock
        if size.stock < quantity:
            return JsonResponse({'error': 'Not enough items in stock'}, status=400)
        
        # Get cart
        cart = get_cart(request)
        
        # Add to cart or update existing item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            if cart_item.quantity > size.stock:
                cart_item.quantity = size.stock
            cart_item.save()
        
        # Return updated cart info
        return JsonResponse({
            'success': True,
            'cart_total': str(cart.get_total_cost()),
            'cart_items_count': cart.items.count(),
        })
        
    except (Product.DoesNotExist, ShoeSize.DoesNotExist):
        return JsonResponse({'error': 'Product or size not found'}, status=404)


def cart_view(request):
    """View cart contents"""
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def cart_update(request):
    """Update cart item quantity"""
    data = json.loads(request.body)
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))
    
    try:
        cart = get_cart(request)
        item = CartItem.objects.get(id=item_id, cart=cart)
        
        if quantity > 0 and quantity <= item.size.stock:
            item.quantity = quantity
            item.save()
            
            # Return updated cart info
            return JsonResponse({
                'success': True,
                'item_total': str(item.get_cost()),
                'cart_total': str(cart.get_total_cost()),
            })
        elif quantity <= 0:
            # Remove item if quantity is zero or negative
            item.delete()
            return JsonResponse({
                'success': True,
                'removed': True,
                'cart_total': str(cart.get_total_cost()),
                'cart_items_count': cart.items.count(),
            })
        else:
            return JsonResponse({'error': 'Requested quantity exceeds available stock'}, status=400)
            
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)


@require_POST
def cart_remove(request):
    """Remove an item from cart"""
    data = json.loads(request.body)
    item_id = data.get('item_id')
    
    try:
        cart = get_cart(request)
        item = CartItem.objects.get(id=item_id, cart=cart)
        item.delete()
        
        return JsonResponse({
            'success': True,
            'cart_total': str(cart.get_total_cost()),
            'cart_items_count': cart.items.count(),
        })
        
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)


def checkout(request):
    """Display checkout form"""
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    # Redirect to cart if empty
    if not cart_items:
        return redirect('store:cart_view')
    
    # Pre-fill form with user data if authenticated
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'initial': initial_data,
    }
    return render(request, 'store/checkout.html', context)


@require_POST
def place_order(request):
    """Process checkout form and place order"""
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    # Redirect to cart if empty
    if not cart_items:
        return redirect('store:cart_view')
    
    # Process form data
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        note = request.POST.get('note', '')
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Simple validation
        if not all([first_name, last_name, email, phone, address, city, postal_code]):
            return render(request, 'store/checkout.html', {
                'cart': cart,
                'cart_items': cart_items,
                'error': 'Будь ласка, заповніть всі обов\'язкові поля',
            })
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            note=note,
            total_cost=cart.get_total_cost()
        )
        
        # Create order items and update stock
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.product.price,
                quantity=cart_item.quantity,
                size=cart_item.size.size
            )
            
            # Update product stock
            size = cart_item.size
            size.stock -= cart_item.quantity
            size.save()
        
        # Clear cart
        cart.items.all().delete()
        
        # Clear cart from session
        if 'cart_id' in request.session:
            del request.session['cart_id']
        
        # If card payment is selected, redirect to payment page
        if payment_method == 'card':
            return redirect('store:payment', order_id=order.id)
        
        # Otherwise redirect to order confirmation page
        return redirect('store:order_confirmation', order_id=order.id)


def order_confirmation(request, order_id):
    """Display order confirmation after successful checkout"""
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, 'store/order_confirmation.html', {
            'order': order,
            'order_items': order_items,
            'show_actions': True
        })
    except Order.DoesNotExist:
        return redirect('store:index')