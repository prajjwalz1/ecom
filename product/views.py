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
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from .models import Brand, Tag, Category, Specification, CarouselImage, Navbar
from .serializers import BrandSerializer, TagSerializer, CategorySerializer, SpecificationSerializer, CarouselImageSerializer, NavbarSerializer
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class HomeView(ResponseMixin,APIView):
    def get(self,request):
        request_type=request.GET.get("request_type")
        if request_type=="tagged_product":
            return self.TaggedProduct(request)
        if request_type=="all_tagged_product":
            return self.AllTaggedProduct(request)
        else:
            return ResponseMixin.handle_error_response(error_message="bad request",status_code=400)

    def getnavbar(self,request):
        obj = Navbar.objects.prefetch_related('category').all()
        serializer=NavbarSerializer(obj,many=True,context={"request":request})
        return serializer.data
    def get_carousel_images(self,request):
        images=CarouselImage.objects.all()
        serializer=CarouselImageSerializer(images,many=True,context={"request":request})
        return serializer.data
    def AllTaggedProduct(self, request):
        # Fetch all tags with related products
        tags = Tag.objects.prefetch_related(
            'products',                      # Prefetch related products
            'products__brand',               # Prefetch related brand for each product
            'products__category',            # Prefetch related category for each product
            'products__variants',            # Prefetch related variants for each product
            'products__variants__productvariantsimages'  # Prefetch related images for each variant
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
        brands=Brand.objects.all()
        brands_serializer=BrandSerializer(brands,context={"request":request},many=True)

        # Final response structure
        response_data = {
            'section_wise_product': section_wise_data,
            'navbar': self.getnavbar(request),
            'carousel': self.get_carousel_images(request),
            'brands':brands_serializer.data
        }

        # Return the response using your custom success handler
        return ResponseMixin.handle_success_response(serialized_data=response_data, status_code=200)

class ProductDetailView(ResponseMixin,APIView,GetSingleObjectMixin):

    def get(self,request):
        request_type=request.GET.get("request")
        product_id=request.GET.get("product_id")
        if request_type=="get_product_detail":
            return self.get_product_detail(request,product_id)
        else:
            return ResponseMixin.handle_error_response(error_message="request is not valid",status_code=400)
    
    def get_product_detail(self,request,id):
        query={"id":id}
        obj,error=self.get_object(Product,**query)
        # breakpoint()
        serializer=ProductSerializer(obj,context={"request":request})
        return ResponseMixin.handle_success_response(serialized_data=serializer.data,status_code=200)
        breakpoint()

class BrandView(ResponseMixin,APIView):
    def get(self,request):
        request_type=request.GET.get("request")
        if request_type=="get_all_brands":
            return self.AllBrands(request)
        else:
            return ResponseMixin.handle_error_response(error_message="bad request",status_code=400)
    
    def AllBrands(self,request):
        qs=Brand.objects.all()
        serializer=BrandSerializer(qs,context={"request":request},many=True)
        return ResponseMixin.handle_success_response(serialized_data=serializer.data,message="brands retrieved successfully",status_code=200)
    
class CategoryWiseProduct(APIView,ResponseMixin):
    def get(self,request):
        request_type=request.GET.get("request")
        if request_type=="category_wise_product":
            return self.CategoryWiseProduct(request)
        else:
            return ResponseMixin.handle_error_response(error_message="bad request",status_code=400)
    def CategoryWiseProduct(self, request):
        category_id = request.GET.get("category_id")
        
        try:
            # Get the main category
            main_category = Category.objects.get(id=category_id)
            print(main_category)
            # Get IDs of the main category and its child categories
            child_category_ids = Category.objects.filter(parent_category=main_category).values_list('id', flat=True)
            category_ids = list(child_category_ids) + [main_category.id]  # Include the main category ID
            print(child_category_ids)
            # Fetch products based on the category IDs
            products = Product.objects.filter(category_id__in=category_ids).select_related('brand').prefetch_related("variants",'variants__productvariantsimages')

            serializer = ProductSerializer(products, many=True, context={"request": request})

            return ResponseMixin.handle_success_response(
                serialized_data=serializer.data,
                status_code=200,
                message="Products fetched successfully"
            )

        except Category.DoesNotExist:
            return ResponseMixin.handle_success_response(
                serialized_data=[],
                status_code=404,
                message="Category not found"
            )

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
        ).distinct()
        
        # for result in results:
        #     print(result.product_name)
        # breakpoint()

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

        return ResponseMixin.handle_paginated_response(
            status_code=200,
            serialized_data=serializer.data,
            page_obj=page_obj  # Pass paginator for pagination info
        )
    

class ProductReviewView(APIView,ResponseMixin):
    def post(self,request):
        request_type=request.GET.get('request')
        if request_type =="post_review":
            return self.post_review(request)
        if request_type =="reply_review":
            return self.reply_review(request)
        else:
            return Response({"error": "Invalid request type"}, status=400)
    def get(self,request):
        request_type=request.GET.get('request')
        if request_type =="get_product_review":
            return self.get_product_review(request)
        else:
            return Response({"error": "Invalid request type"}, status=400)
    def post_review(self,request):
        data=request.data
        review_serializer=ReviewSerializer(data=data)
        if review_serializer.is_valid():
            review_serializer.save()
            print("sssssssssssssss")            
            return ResponseMixin.handle_success_response(message="product review added successfully",status_code=200)
        else:
            return ResponseMixin.handle_serializererror_response(serializer_errors=review_serializer.errors,status_code=400)
    def reply_review(self,request):
        data=request.data
        review_serializer=ReplyReviewSerializer(data=data)
        if review_serializer.is_valid():
            review_serializer.save()
            print("sssssssssssssss")            
            return ResponseMixin.handle_success_response(message="product review added successfully",status_code=200)
        else:
            return ResponseMixin.handle_serializererror_response(serializer_errors=review_serializer.errors,status_code=400)
        
    def get_product_review(self,request):
        review=ProductReview.objects.filter(product=request.GET.get("product_id")).prefetch_related('replies')
        review_serializer=GETReviewSerializer(review,many=True)

                   
        return ResponseMixin.handle_success_response(message="product review added successfully",status_code=200,serialized_data=review_serializer.data)
       
class BrandWiseProducts(APIView,ResponseMixin):
    def get(self,request):
        request_type=request.GET.get("request")
        if request_type=="brandwise_product":
            return self.BrandwiseProduct(request)
        
    def BrandwiseProduct(self,request):
        brand_id=request.GET.get("brand_id")
        if not brand_id:
            return self.handle_error_response(error_message="brand id not sent in query",status_code=400)
        qs=Product.objects.filter(brand_id=brand_id)
        serializer=ProductSerializer(qs,many=True,context={"request":request})
        return self.handle_success_response(serialized_data=serializer.data,status_code=200)
    


class ProductCRUD(APIView,ResponseMixin):
    authentication_classes = [JWTAuthentication] # Ensure user is authenticated
    def post(self,request):
        request_type=request.GET.get("request")
        if request_type=="AddProduct":
            return self.AddProduct(request)
    def AddProduct(self,request):
        data=request.data
        # print(data)
        serializer=ProductAddSerializer(data=data,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return self.handle_success_response(serialized_data=serializer.data,status_code=200,message="product added successfully")
        else:
            return Response({"success":False,"message":serializer.errors})



class ProductDependencies(APIView,ResponseMixin):
    authentication_classes = [JWTAuthentication] # Ensure user is authenticated

    def get(self,request):
        request_type=request.GET.get("request")
        if request_type=="get-brands-cat-tags":
            return self.ProductCrudDependencies(request)
        else:
            return self.handle_error_response(error_message="bad request type",status_code=400)
            

    
    def ProductCrudDependencies(self,request):
        categories = Category.objects.all()
        brands = Brand.objects.all()
        tags = Tag.objects.all()
        colors=VariantColors.objects.all()

        # Serialize related data
        categories_data = CategorySerializer(categories, many=True).data
        brands_data = BrandSerializer(brands, many=True).data
        tags_data = GetTagSerializer(tags, many=True).data
        colors_data = ProductVaraintColorSerializer(colors, many=True).data

        response_data = {

            'categories': categories_data,
            'brands': brands_data,
            'tags': tags_data,
            'colors':colors_data
        }

        return self.handle_success_response(serialized_data=response_data,status_code=200,message="success")



class CategorySpecificationsView(APIView,ResponseMixin):
    authentication_classes = [JWTAuthentication] # Ensure user is authenticated

    def get(self, request):
        category_id=request.GET.get("category_id")
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the root category
        root_category = category.get_root_category()

        # Fetch specifications for the root category
        specifications = Specification.objects.filter(category=root_category)
        serializer = SpecificationSerializer(specifications, many=True)

        return self.handle_success_response(serialized_data=serializer.data,status_code=200,message="success")
    



# Brand API Views
class BrandListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = PageNumberPagination

class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

# Tag API Views
class TagListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = GenericsTagSerializer
    pagination_class = PageNumberPagination

class TagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = GenericsTagSerializer

# Category API Views
class CategoryListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Specification API Views
class SpecificationListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer
    pagination_class = PageNumberPagination

class SpecificationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer

# CarouselImage API Views
class CarouselImageListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselImageSerializer
    pagination_class = PageNumberPagination

class CarouselImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselImageSerializer

# Navbar API Views
class NavbarListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Navbar.objects.all()
    serializer_class = GenericsNavbarSerializer
    pagination_class = PageNumberPagination


class NavbarRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Navbar.objects.all()
    serializer_class = GenericsNavbarSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductAddSerializer
    pagination_class = PageNumberPagination


class ColorsListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = VariantColors.objects.all()
    serializer_class = ProductVaraintColorSerializer
    pagination_class = PageNumberPagination

class ColorsUpdateDistroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = VariantColors.objects.all()
    serializer_class = ProductVaraintColorSerializer
    pagination_class = PageNumberPagination

class ProductRetrieveUpdateDestroyView(ResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = GenericsProductAddSerializer

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        serialized_data = self.get_serializer(product).data
        return self.handle_success_response(
            status_code=status.HTTP_200_OK,
            serialized_data=serialized_data
        )

    def put(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.handle_success_response(
                status_code=status.HTTP_200_OK,
                serialized_data=serializer.data,
                message="Product updated successfully"
            )
        else:
            return self.handle_serializererror_response(
                serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return self.handle_success_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Product deleted successfully"
        )
    

class ProductImageCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    pagination_class = PageNumberPagination

class ProductImageWithoutVariantCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductParentImage.objects.all()
    serializer_class = ProductImageWithoutVariantSerializer
    pagination_class = PageNumberPagination
   
class ProductImageWithoutVariantUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductParentImage.objects.all()
    serializer_class = ProductImageWithoutVariantSerializer


class ProductImageUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class ProductVariantListCreateView(generics.ListCreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductVariant.objects.all()
    serializer_class = ProductGenericsVariantSerializer
    pagination_class = PageNumberPagination


class ProductVariantUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductVariant.objects.all()
    serializer_class = ProductGenericsVariantSerializer
    pagination_class = PageNumberPagination
