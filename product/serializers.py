from rest_framework import serializers
from .models import *

class TaggedProductSerializer(serializers.Serializer):
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']  # Include fields you want to display

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description','image']  # Include fields you want to display

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image', 'alt_text']
    
class ProductVariantSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()  # Use SerializerMethodField for images

    class Meta:
        model = ProductVariant
        fields = ['id', 'price','variant_name', 'color_code', 'color_name', 'ram', 'rom', 'discount_price', 'images']

    def get_images(self, obj):
        # Use the ProductImageSerializer to serialize related images
        return ProductImageSerializer(obj.productvariantsimages.all(), many=True,context=self.context).data  # Serialize images directly

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = serializers.SerializerMethodField()  # Assuming images are linked directly to Product
    variants = ProductVariantSerializer(many=True, read_only=True)  # Include variants for price access
    brand_id = serializers.CharField(source='brand.id', allow_null=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name','brand_id','stock','details', 'product_description', 'images', 'category', 'brand', 'variants']

    def get_price(self, obj):
        # Optionally return the price of the first variant, adjust as necessary
        if obj.variants.exists():
            return obj.variants.first().price
        return None

    def get_discount_price(self, obj):
        # Optionally return the discount price of the first variant, adjust as necessary
        if obj.variants.exists():
            return obj.variants.first().discount_price
        return None
    def get_images(self, obj):
        # Use a list comprehension to serialize each image
        images = []
        for variant in obj.variants.all():  # Use .all() to get the queryset
            images.extend(ProductImageSerializer(variant.productvariantsimages.all(), many=True,context=self.context).data)  # Serialize the images
        return images
    
class TagSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'products','section']

    def get_products(self, obj):
        # Fetch only the first 8 products related to the tag
        
        products = obj.products.all().order_by('-created_at')[:12]
        return ProductSerializer(products, many=True,context=self.context).data


class GetTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name','section']



    
class CarouselImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=CarouselImage
        fields='__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ParentCategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'subcategories']

    def to_representation(self, instance):
        # Ensure we're only returning parent categories (where parent_category is null)
        if instance.parent_category is None:
            return super().to_representation(instance)
        return None

class NavbarSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Navbar
        fields = ['id', 'name', 'categories']

    def get_categories(self, obj):
        # Get only the parent categories (where parent_category is None)
        parent_categories = obj.category.filter(parent_category__isnull=True)
        return ParentCategorySerializer(parent_categories, many=True).data
    

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(read_only=True)  # Include variants for price access


    class Meta:
        model = Product
        fields = ['id', 'product_name','details', 'specifications', 'product_description', 'images','variants', 'category', 'brand', 'stock']

    def get_specifications(self, obj):
        # Fetch all category-level specifications
        category_specifications = Specification.objects.filter(category=obj.category)
        
        # Fetch product-specific specifications
        product_specifications = ProductSpecification.objects.filter(product=obj)

        # Create a dictionary for easier lookup
        product_spec_map = {ps.spec_name.id: ps for ps in product_specifications}

        # Build the final list of specifications
        result = []
        for category_spec in category_specifications:
            product_spec = product_spec_map.get(category_spec.id)

            result.append({
                'spec_name': category_spec.spec_name,  # Directly use the spec_name field
                'value': product_spec.value if product_spec else None,  # Use product value or placeholder
                'value_unit': product_spec.value_unit if product_spec else None  # Placeholder if unit not available
            })
        
        return result
    

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields="__all__"

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductReview
        fields = ['id','product', 'review']

class ReplyReviewSerializer(serializers.ModelSerializer):
    # Assuming `review` is a ForeignKey field in ProductReview
    review = serializers.PrimaryKeyRelatedField(queryset=ProductReview.objects.all())

    class Meta:
        model = ProductReviewReply
        fields = ['review', 'reply']


class GETReviewSerializer(serializers.ModelSerializer):
    replies = ReplyReviewSerializer(many=True, read_only=True)  # Use the related name from the Reply model

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'review', 'replies']


from .models import (
    Category, Brand, Tag, Specification, Product,
    ProductVariant, ProductVariantPriceHistory, ProductImage,
    ProductSpecification
)

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'description', 'parent_category', 'subcategories']
        
# class BrandSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Brand
#         fields = ['id', 'name', 'image', 'description']

# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ['id', 'name', 'section', 'priority']

class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['id', 'spec_name', 'category']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'productvariant', 'image', 'alt_text']

class ProductVariantPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantPriceHistory
        fields = ['id', 'variant', 'price', 'discount_price', 'date_added']

from django.core.files.base import ContentFile
import base64
import imghdr
from io import BytesIO

# class ProductSpecificationSerializer(serializers.ModelSerializer):
#     spec_name = SpecificationSerializer()

#     class Meta:
#         model = ProductSpecification
#         fields = ['id', 'product', 'spec_name', 'value', 'value_unit']



class Base64ImageField(serializers.ImageField):
    """
    Custom serializer field to handle Base64-encoded images.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                # Separate the header from the base64 data
                header, data = data.split('data:image/', 1)
                format, data = data.split(';base64,', 1)
                if format == "jpeg":
                    format = "jpg"
            except ValueError:
                raise serializers.ValidationError("Invalid Base64 data")

            decoded_file = base64.b64decode(data)
            file_name = f"temp.{format}"
            file = ContentFile(decoded_file, name=file_name)
            return file
        return super().to_internal_value(data)

class ProductImageAddSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']


class ProductVariantSerializer(serializers.ModelSerializer):
    productvariantsimages = ProductImageAddSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = [
            'variant_name', 'color_code', 'color_name', 'rom',
            'ram', 'price', 'discount_price', 'productvariantsimages'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['productvariantsimages'].context.update(self.context)

    def create(self, validated_data):
        images_data = validated_data.pop('productvariantsimages', [])
        product_variant = ProductVariant.objects.create(**validated_data)
        ProductImage.objects.bulk_create(
            [ProductImage(productvariant=product_variant, **image_data) for image_data in images_data]
        )
        return product_variant

class ProductAddSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    variants = ProductVariantSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'product_name', 'product_description', 'category', 'brand',
            'stock', 'tags', 'details', 'variants'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['variants'].context.update(self.context)

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        tags_data = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        product.tags.set(tags_data)

        for variant_data in variants_data:
            images_data = variant_data.pop('productvariantsimages', [])
            product_variant = ProductVariant.objects.create(product=product, **variant_data)
            ProductImage.objects.bulk_create(
                [ProductImage(productvariant=product_variant, **image_data) for image_data in images_data]
            )

        return product