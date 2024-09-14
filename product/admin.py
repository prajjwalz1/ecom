from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

# Customize the admin interface for each model

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'parent_category')
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


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Allows for adding multiple images in the same form


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1  # Allows adding multiple specifications in the same form


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'brand', 'price', 'stock')
    search_fields = ('product_name', 'category__name', 'brand__name')
    list_filter = ('category', 'brand', 'tags')
    inlines = [ProductImageInline, ProductSpecificationInline]

    fieldsets = (
        (None, {
            'fields': ('product_name', 'product_description', 'category', 'brand', 'price', 'discount_price', 'stock', 'tags')
        }),
    )


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'spec_name', 'value')
    search_fields = ('product__product_name', 'spec_name__spec_name')
    list_filter = ('spec_name',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'alt_text')
    search_fields = ('product__product_name',)


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
