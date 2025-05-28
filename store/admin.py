from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    ShoeCategory, Product, ProductImage, ShoeSize, 
    Cart, CartItem, Order, OrderItem
)

class ShoeSizeInline(admin.TabularInline):
    model = ShoeSize
    extra = 6  # Show 6 empty forms by default for common shoe sizes

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Show 3 empty forms by default

@admin.register(ShoeCategory)
class ShoeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_image', 'gender', 'shoe_type', 'price', 'available']
    list_filter = ['available', 'created', 'gender', 'shoe_type', 'category']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ShoeSizeInline, ProductImageInline]
    search_fields = ['name', 'description']
    save_as = True  # Adds "Save as new" button to easily duplicate products
    save_on_top = True  # Adds save buttons at the top of the change form
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'
    
    def save_model(self, request, obj, form, change):
        """Override to provide default values or post-save actions"""
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only in edit mode but editable in add mode"""
        if obj:  # Editing an existing object
            return []
        return []

    actions = ['duplicate_product']

    def duplicate_product(self, request, queryset):
        """Action to duplicate selected products"""
        for product in queryset:
            # Create a duplicate product
            product.pk = None
            product.name = f"Copy of {product.name}"
            product.slug = f"{product.slug}-copy"
            product.save()
            
            # Duplicate related sizes
            sizes = ShoeSize.objects.filter(product__slug=product.slug.replace('-copy', ''))
            for size in sizes:
                ShoeSize.objects.create(
                    product=product,
                    size=size.size,
                    stock=size.stock
                )
                
            # Duplicate related images (except main product image)
            images = ProductImage.objects.filter(product__slug=product.slug.replace('-copy', ''))
            for img in images:
                ProductImage.objects.create(
                    product=product,
                    image=img.image,
                    is_main=img.is_main,
                    order=img.order
                )
                
        self.message_user(request, f"Successfully duplicated {queryset.count()} product(s).")
    duplicate_product.short_description = "Duplicate selected products"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at', 'get_total_items', 'get_total']
    search_fields = ['id', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_filter = ['created_at']
    
    def get_total_items(self, obj):
        return obj.items.count()
    get_total_items.short_description = 'Total Items'
    
    def get_total(self, obj):
        return f"{obj.get_total_cost()} грн"
    get_total.short_description = 'Total Cost'
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'size', 'quantity', 'get_cost']
    list_filter = ['cart__created_at']
    search_fields = ['product__name', 'cart__user__username']
    
    def get_cost(self, obj):
        return f"{obj.get_cost()} грн"
    get_cost.short_description = 'Cost'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_customer_name', 'status', 'total_cost', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', ('first_name', 'last_name'), ('email', 'phone'))
        }),
        ('Shipping Information', {
            'fields': ('address', ('city', 'postal_code'), 'note')
        }),
        ('Order Information', {
            'fields': ('status', 'total_cost', ('created_at', 'updated_at'))
        }),
    )
    
    def get_customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_customer_name.short_description = 'Customer'
    
    def view_items(self, obj):
        url = reverse('admin:store_orderitem_changelist')
        return format_html('<a href="{}?order__id__exact={}">View Items</a>', url, obj.id)
    view_items.short_description = 'Items'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity', 'size', 'get_cost']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__id', 'product__name']
    
    def get_cost(self, obj):
        return f"{obj.get_cost()} грн"
    get_cost.short_description = 'Cost'