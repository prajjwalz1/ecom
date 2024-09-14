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
    def TaggedProduct(self,request):
        tag=request.data.get("tag")
        data={
            "tag":tag
        }
        serializer=TaggedProductSerializer(data=data)
        if serializer.is_valid():
            obj=Tag.objects.prefetch_related('products__brand','products__category').get(id=tag)
            serializer=TagSerializer(obj,context={"request":request})
            return self.handle_success_response(message="products fteched successfully",serialized_data=serializer.data,status_code=200)
        
        else:
            return self.handle_serializererror_response(error_messages=serializer.errors,status_code=400)

    def getnavbar(self,request):
        obj=Navbar.objects.prefetch_related('category').all()
        serializer=NavbarSerializer(obj,many=True,context={"request":request})
        return serializer.data
    def get_carousel_images(self,request):
        images=CarouselImage.objects.all()
        serializer=CarouselImageSerializer(images,many=True,context={"request":request})
        return serializer.data
    def AllTaggedProduct(self,request):
        tag=Tag.objects.prefetch_related('products','products__brand','products__category','products__images').all()
        serializer=MultiTagSerializer(tag,many=True,context={"request":request})
        data=serializer.data[0]
        # breakpoint()
        data["navbar"]=self.getnavbar(request)
        data["carousel"]=self.get_carousel_images(request)
        return self.handle_success_response(message="products fteched successfully",serialized_data=data,status_code=200)
        


class CarouselAPI(ResponseMixin,APIView):
    
    def get_images(self,request):
        images=CarouselImage.objects.all()
        serializer=CarouselImageSerializer(images,many=True,context={"request":request})
        return self.handle_success_response(status_code=200,serialized_data=serializer.data,message="carousel images fetched successfully")