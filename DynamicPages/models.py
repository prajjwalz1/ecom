from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
from django.db import models
from product.mixins import *
from product.models import Product


class DynamicPage(models.Model):
    """
    Model to store dynamic HTML content for rendering pages.
    """

    title = models.CharField(
        max_length=255, unique=True, help_text="Title of the page."
    )
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Slug for the page URL."
    )
    content = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the page was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the page was last updated."
    )

    def __str__(self):
        return self.title


class HappyCustomer(CustomizedModel):
    """
    Model to store dynamic HTML content for rendering pages.
    """

    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_photo = models.ImageField(upload_to="customers")
    customer_review = models.TextField(null=True, blank=True)
    product_bought = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.customer_name
