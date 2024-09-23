from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .mixins import *
from .serializers import *
from .models import Product,CarouselImage
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Tag, Category, Brand


class HomeView(ResponseMixin,APIView):
    def get(self,request):
        request_type=request.GET.get("request_type")
        if request_type=="tagged_product":
            return self.TaggedProduct(request)
        if request_type=="all_tagged_product":
            return self.AllTaggedProduct(request)
        else:
            return self.handle_error_response(error_message="bad request",status_code=400)

    def getnavbar(self,request):
        obj=Navbar.objects.prefetch_related('category').all()
        serializer=NavbarSerializer(obj,many=True,context={"request":request})
        return serializer.data
    def get_carousel_images(self,request):
        images=CarouselImage.objects.all()
        serializer=CarouselImageSerializer(images,many=True,context={"request":request})
        return serializer.data
    def AllTaggedProduct(self, request):
        # Fetch all tags with related products
        tags = Tag.objects.prefetch_related(
            'products', 'products__brand', 'products__category', 'products__images'
        ).all().order_by('priority', '-last_modified')

        # Serialize the tags with their related products
        serializer = TagSerializer(tags, many=True, context={"request": request})
        serialized_data = serializer.data

        # Initialize the data structure categorized by section
        section_wise_data = {}

        for tag in serialized_data:
            # Extract relevant fields from the serialized data
            section_name = tag['section']  # Get the section name
            tag_name = tag['name']         # Get the tag name
            products = tag['products']     # Get the products under the tag

            # Group tags and their products under sections
            if section_name not in section_wise_data:
                section_wise_data[section_name] = []  # Initialize a new section
            
            # Add the tag and its products to the section
            section_wise_data[section_name].append({
                "tag_name": tag_name,
                "products": products
            })

        # Final response structure
        response_data = {
            'section_wise_product': section_wise_data,
            'navbar': self.getnavbar(request),
            'carousel': self.get_carousel_images(request),
        }

        # Return the response using your custom success handler
        return self.handle_success_response(serialized_data=response_data, status_code=200)

class ProductDetailView(ResponseMixin,APIView,GetSingleObjectMixin):

    def get(self,request):
        request_type=request.GET.get("request")
        product_id=request.GET.get("product_id")
        if request_type=="get_product_detail":
            return self.get_product_detail(request,product_id)
        else:
            return self.handle_error_response(error_message="request is not valid",status_code=400)
    
    def get_product_detail(self,request,id):
        query={"id":id}
        obj,error=self.get_object(Product,**query)
        # breakpoint()
        serializer=ProductDetailSerializer(obj,context={"request":request})
        return self.handle_success_response(serialized_data=serializer.data,status_code=200)
        breakpoint()

class BrandView(ResponseMixin,APIView):
    def get(self,request):
        request_type=request.GET.get("request")
        if request_type=="get_all_brands":
            return self.AllBrands(request)
        else:
            return self.handle_error_response(error_message="bad request",status_code=400)
    
    def AllBrands(self,request):
        qs=Brand.objects.all()
        serializer=BrandSerializer(qs,context={"request":request},many=True)
        return self.handle_success_response(serialized_data=serializer.data,message="brands retrieved successfully",status_code=200)
    
class CategoryWiseProduct(APIView,ResponseMixin):
    def get(self,request):
        request_type=request.GET.get("request")
        if request_type=="category_wise_product":
            return self.CategoryWiseProduct(request)
        else:
            return self.handle_error_response(error_message="bad request",status_code=400)
    def CategoryWiseProduct(self,request):
        category_id=request.GET.get("category_id")
        print(category_id)
        obj=Product.objects.filter(category=category_id).select_related('brand').prefetch_related("images")
        serializer=ProductSerializer(obj,many=True,context={"request":request})
        return self.handle_success_response(serialized_data=serializer.data,status_code=200,message="products fetched successfully")
        # breakpoint()


class SearchProduct(APIView,ResponseMixin):
    def get(self,request):
        query = request.GET.get('q', '')
        price_min = request.GET.get('price_min', 0)
        price_max = request.GET.get('price_max', 1000000)
        category = request.GET.get('category', None)
        brand = request.GET.get('brand', None)

        # Build the base query
        results = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(product_description__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        ).filter(
            price__gte=price_min,
            price__lte=price_max,
            stock__gte=1  # Only show products that are in stock
        )

        # Filter by category if provided
        if category:
            results = results.filter(category__name__icontains=category)

        # Filter by brand if provided
        if brand:
            results = results.filter(brand__name__icontains=brand)


        paginator = Paginator(results, 10)  # Show 10 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Serialize the paginated results
        serializer = ProductSerializer(page_obj, many=True,context={"request":request})

        return self.handle_paginated_response(
            status_code=200,
            serialized_data=serializer.data,
            page_obj=page_obj  # Pass paginator for pagination info
        )