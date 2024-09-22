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
    image=serializers.SerializerMethodField()
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']
    def get_image(self,obj):
        if obj.image:
            request=self.context.get("request")
            image=obj.image.url
            if request is not None:
                return request.build_absolute_uri(image)
            return image
        return None

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_description','images', 'category', 'brand', 'price', 'discount_price', 'stock']
    


class TagSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'products','section']

    def get_products(self, obj):
        # Fetch only the first 8 products related to the tag
        
        products = obj.products.all()
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

    class Meta:
        model = Product
        fields = ['id', 'product_name','details', 'specifications', 'product_description', 'images', 'category', 'brand', 'price', 'discount_price', 'stock']

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