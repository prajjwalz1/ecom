from rest_framework import serializers
from .models import DynamicPage, HappyCustomer


class DynamicPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicPage
        fields = ["id", "title", "slug", "content", "created_at", "updated_at"]


class HappyCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HappyCustomer
        fields = "__all__"
