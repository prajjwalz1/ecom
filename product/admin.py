from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

# Customize the admin interface for each model

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'description', 'parent_category')
    search_fields = ('name',)
    list_filter = ('parent_category',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('spec_name',)
    search_fields = ('spec_name',)


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1  # Allows for adding multiple images in the same form


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1  # Allows adding multiple specifications in the same form


class ProductVariantPriceHistoryInline(admin.TabularInline):
    model = ProductVariantPriceHistory
    extra = 0
    readonly_fields = ('price', 'discount_price', 'date_added')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ['product', 'variant_name', 'rom', 'ram', 'price', 'discount_price']
    fields= ['product', 'rom', 'ram', 'price', 'discount_price']

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields=['rom','ram','price','discount_price','color_available']



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'brand', 'stock')
    search_fields = ('product_name', 'category__name', 'brand__name')
    list_filter = ('category', 'brand', 'tags')
    inlines = [ProductVariantInline]

    fieldsets = (
        (None, {
            'fields': (
                'product_name', 
                'product_description', 
                'category', 
                'brand', 
                'stock', 
                'tags',
                'details'
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand')

    def save_model(self, request, obj, form, change):
        logger.info(f"Admin saving Product: {obj.product_name}")
        super().save_model(request, obj, form, change)

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'spec_name', 'value')
    search_fields = ('product__product_name', 'spec_name__spec_name')
    list_filter = ('spec_name',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('productvariant', 'image', 'alt_text')
    search_fields = ('productvaraint__product_name',)


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    ordering = ('order',)


@admin.register(Navbar)
class NavbarAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    filter_horizontal = ['category']  # ManyToMany field to display categories



admin.site.register(VariantColors)
admin.site.register(ProductParentImage)