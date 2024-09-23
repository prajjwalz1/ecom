from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .mixins import *
from .serializers import *
from .models import Product,CarouselImage



class HomeView(ResponseMixin,APIView):
    def get(self,request):
        request_type=request.GET.get("request_type")
        if request_type=="tagged_product":
            return self.TaggedProduct(request)
        if request_type=="all_tagged_product":
            return self.AllTaggedProduct(request)
        else:
            return self.handle_error_response(error_message="bad request",status_code=400)
    # def TaggedProduct(self,request):
    #     tag=request.data.get("tag")
    #     data={
    #         "tag":tag
    #     }
    #     serializer=TaggedProductSerializer(data=data)
    #     if serializer.is_valid():
    #         obj=Tag.objects.prefetch_related('products__brand','products__category').get(id=tag)
    #         serializer=TagSerializer(obj,context={"request":request})
    #         return self.handle_success_response(message="products fteched successfully",serialized_data=serializer.data,status_code=200)
        
    #     else:
    #         return self.handle_serializererror_response(error_messages=serializer.errors,status_code=400)

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
        ).all().order_by('priority', '-last_modified')[:8]

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
        obj=Product.objects.filter(Category__id=category_id).select_related("category")
