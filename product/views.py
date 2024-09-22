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
        tag=Tag.objects.prefetch_related('products','products__brand','products__category','products__images').all()        
        # Serialize the tags with their related products
        serializer = TagSerializer(tag, many=True,context={"request":request})
        serialized_data = serializer.data

        # Transform the serialized data into the desired format
        data = {}
        for tag in serialized_data:
            tag_name = tag['name']
            products = tag['products']
            data[tag_name] = products

        # Structure the final response
        response_data = {
            'products': data,
            'navbar': self.getnavbar(request),
            'carousel': self.get_carousel_images(request),
        }

        return self.handle_success_response(serialized_data=response_data,status_code=200)


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