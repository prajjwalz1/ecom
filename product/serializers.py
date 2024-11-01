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