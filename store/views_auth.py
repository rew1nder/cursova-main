from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistrationForm, UserProfileForm
from .models import Order, OrderItem
from .views import get_cart

def login_view(request):
    """View for user login"""
    if request.user.is_authenticated:
        return redirect('store:product_list')
    
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Get session-based cart and associate it with user
                cart = get_cart(request)
                if cart.user is None:
                    cart.user = user
                    cart.save()
                
                # Redirect to next URL if provided, otherwise to homepage
                if next_url:
                    return redirect(next_url)
                return redirect('store:product_list')
            
        messages.error(request, 'Неправильне ім\'я користувача або пароль')
    else:
        form = LoginForm()
    
    return render(request, 'store/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    """View for user logout"""
    logout(request)
    messages.success(request, 'Ви успішно вийшли з облікового запису')
    return redirect('store:product_list')

def register_view(request):
    """View for user registration"""
    if request.user.is_authenticated:
        return redirect('store:product_list')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            # Get session-based cart and associate it with user
            cart = get_cart(request)
            if cart.user is None:
                cart.user = user
                cart.save()
                
            messages.success(request, 'Обліковий запис успішно створено!')
            return redirect('store:product_list')
    else:
        form = RegistrationForm()
    
    return render(request, 'store/register.html', {'form': form})

@login_required
def profile_view(request):
    """View for user profile management"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено')
            return redirect('store:profile')
    else:
        form = UserProfileForm(instance=user)
    
    # Get user's order history
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'store/profile.html', {
        'form': form,
        'orders': orders,
        'user': user
    })

@login_required
def order_detail_view(request, order_id):
    """View for displaying order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'order_items': order_items,
        'show_actions': False  # Don't show action buttons for order history
    })

@login_required
def payment_view(request, order_id):
    """View for payment processing"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is already paid
    if order.status != 'pending':
        messages.info(request, 'Це замовлення вже оплачено')
        return redirect('store:order_confirmation', order_id=order.id)
    
    context = {
        'order': order,
        'payment_methods': [
            {'id': 'credit_card', 'name': 'Кредитна картка'},
            {'id': 'paypal', 'name': 'PayPal'},
            {'id': 'google_pay', 'name': 'Google Pay'},
            {'id': 'apple_pay', 'name': 'Apple Pay'}
        ]
    }
    
    return render(request, 'store/payment.html', context)

@login_required
@require_POST
def payment_process(request):
    """Process payment"""
    order_id = request.POST.get('order_id')
    payment_method = request.POST.get('payment_method')
    
    if not order_id or not payment_method:
        messages.error(request, 'Відсутні необхідні параметри')
        return redirect('store:profile')
    
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Check if order is already paid
        if order.status != 'pending':
            messages.info(request, 'Це замовлення вже оплачено')
            return redirect('store:order_confirmation', order_id=order.id)
        
        # This would be where you integrate with a real payment processor
        # For simulation purposes, we'll just mark the order as paid
        order.status = 'processing'  # or 'paid'
        order.payment_method = payment_method
        order.save()
        
        messages.success(request, 'Оплата пройшла успішно!')
        return redirect('store:order_confirmation', order_id=order.id)
        
    except Order.DoesNotExist:
        messages.error(request, 'Замовлення не знайдено')
        return redirect('store:profile')
