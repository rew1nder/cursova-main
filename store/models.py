from django.db import models
from django.urls import reverse
from django.conf import settings
import uuid

# Define product gender choices
GENDER_CHOICES = [
    ('M', 'Men'),
    ('W', 'Women'),
    ('K', 'Kids'),
]

# Define shoe type choices
SHOE_TYPE_CHOICES = [
    ('sneakers', 'Sneakers'),
    ('running', 'Running'),
    ('basketball', 'Basketball'),
    ('casual', 'Casual'),
    ('lifestyle', 'Lifestyle'),
    ('football', 'Football'),
    ('tennis', 'Tennis'),
    ('training', 'Training & Gym'),
]

# Define order status choices
ORDER_STATUS_CHOICES = [
    ('pending', 'В обробці'),
    ('processing', 'Обробляється'),
    ('shipped', 'Відправлено'),
    ('delivered', 'Доставлено'),
    ('cancelled', 'Скасовано'),
]

class ShoeCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Shoe Categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(ShoeCategory, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    shoe_type = models.CharField(max_length=50, choices=SHOE_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('name',)
        indexes = [models.Index(fields=['id', 'slug'])]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])
        
    def get_main_image(self):
        if self.image:
            return self.image.url
        product_images = self.images.all()
        if product_images.exists():
            return product_images.first().image.url
        return None

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"Image for {self.product.name} (#{self.order})"


class ShoeSize(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    size = models.DecimalField(max_digits=3, decimal_places=1)
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('product', 'size')
        ordering = ('size',)
    
    def __str__(self):
        return f"{self.product.name} - Size {self.size}"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='carts', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Cart {self.id} for {self.user.username}"
        return f"Cart {self.id}"
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    size = models.ForeignKey(ShoeSize, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product', 'size')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Size {self.size.size})"
    
    def get_cost(self):
        return self.product.price * self.quantity


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store the price at time of purchase
    quantity = models.PositiveIntegerField(default=1)
    size = models.DecimalField(max_digits=3, decimal_places=1)  # Store the size as a value
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Size {self.size})"
    
    def get_cost(self):
        return self.price * self.quantity

