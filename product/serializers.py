from rest_framework import serializers
from .models import Tag,Product,Category,Brand,ProductImage,CarouselImage,Navbar

class TaggedProductSerializer(serializers.Serializer):
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']  # Include fields you want to display

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description']  # Include fields you want to display

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
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'products']



class MultiTagSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['products']

    def get_products(self, obj):
        # Assuming you have a relationship set up from Tag to Product
        products = obj.products.all()
        grouped_products = {}

        for product in products:
            tag_name = obj.name  # Tag name for grouping
            if tag_name not in grouped_products:
                grouped_products[tag_name] = []
            grouped_products[tag_name].append(ProductSerializer(product,context=self.context).data)
        
        return grouped_products
    
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