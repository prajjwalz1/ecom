from django.shortcuts import render

# Create your views here.
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import *
from .serializers import DynamicPageSerializer
from rest_framework.generics import ListAPIView
from rest_framework import generics
from .serializers import *
from rest_framework.pagination import PageNumberPagination


class DynamicPageDetailView(RetrieveAPIView):
    """
    API to retrieve the content of a page by slug.
    """

    serializer_class = DynamicPageSerializer
    lookup_field = "slug"
    queryset = DynamicPage.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except DynamicPage.DoesNotExist:
            raise NotFound("Page not found.")


class DynamicPageListView(ListAPIView):
    """
    API to list all dynamic pages.
    """

    serializer_class = DynamicPageSerializer
    queryset = DynamicPage.objects.all()


class HappyCustomerListCreateView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = HappyCustomer.objects.all()
    serializer_class = HappyCustomerSerializer
    pagination_class = PageNumberPagination


class HappyCustomerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = HappyCustomer.objects.all()
    serializer_class = HappyCustomerSerializer
