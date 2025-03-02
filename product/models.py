from django.db import models
from .mixins import CustomizedModel
from ckeditor.fields import RichTextField
from django.utils import timezone

# Create your models here.
import logging

logger = logging.getLogger(__name__)


class Category(CustomizedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def get_root_category(self):
        visited = set()  # Keep track of visited categories
        category = self
        while category.parent_category is not None:
            if category.id in visited:
                raise ValueError("Circular reference detected in category hierarchy")
            visited.add(category.id)
            category = category.parent_category
        return category


# Brand Model
class Brand(CustomizedModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="Brands", null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Tag Model
class Tag(CustomizedModel):
    section_choices = (
        ("primary_section", "Primary Section"),
        ("secondary_section", "Secondary Section"),
    )
    name = models.CharField(max_length=50)
    section = models.CharField(choices=section_choices, null=True)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Specification(CustomizedModel):
    spec_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.spec_name} "


from rest_framework import serializers
from django.db import transaction


class ProductImages(CustomizedModel):
    product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, blank=True
    )
    image_alt = models.CharField(max_length=255, null=True, blank=True)
    product_image = models.ImageField(
        upload_to="products/images/", null=False, blank=True
    )


class Product(CustomizedModel):
    product_name = models.CharField(max_length=255, null=False, blank=True)
    product_description = models.TextField(null=False, blank=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    stock = models.IntegerField()
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    details = RichTextField(null=True, blank=True)
    product_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    has_variant = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.product_name

    def save(self, *args, **kwargs):
        logger.info(
            f"Saving Product: {self.product_name} with description: {self.product_description}"
        )
        super().save(*args, **kwargs)


class VariantColors(CustomizedModel):
    color = models.CharField(max_length=255, null=False, blank=False)
    color_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.color


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    variant_name = models.CharField(max_length=255, null=True, blank=True)
    color_available = models.ManyToManyField(VariantColors, blank=True)
    rom = models.CharField(max_length=255, null=True, blank=True)
    ram = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        # Automatically set variant_name based on the presence of rom, ram
        if self.rom and self.ram:
            self.variant_name = f"{self.rom}/{self.ram}"
        elif self.rom:
            self.variant_name = self.rom
        elif self.ram:
            self.variant_name = self.ram
        else:
            self.variant_name = "Unknown Variant"

        super().save(*args, **kwargs)

    def __str__(self):
        # Display the product name along with the variant description (ROM/RAM)
        return f"{self.product.product_name} - {self.variant_name}"


class ProductVariantPriceHistory(CustomizedModel):
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="price_history"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_added"]  # Order by latest price change

    def __str__(self):
        return f"{self.variant} - {self.price} on {self.date_added}"


class ProductImage(CustomizedModel):
    productvariant = models.ForeignKey(
        ProductVariant,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="productvariantsimages",
    )
    image = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.alt_text}"


class ProductParentImage(CustomizedModel):
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="productparentimages",
    )
    product_image = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.alt_text}"


class ProductSpecification(CustomizedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specifications"
    )
    spec_name = models.ForeignKey(Specification, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, null=True, blank=True)
    value_unit = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.product.product_name} - {self.spec_name.spec_name}: {self.value}"


class CarouselImage(CustomizedModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="carousel_images/")
    order = models.PositiveIntegerField(default=0)  # To maintain the order of images
    is_active = models.BooleanField(
        default=True
    )  # Whether the image is currently active in the carousel
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]  # Order by the 'order' field in ascending order

    def __str__(self):
        return self.title or f"Carousel Image {self.id}"


class Navbar(models.Model):
    INTEGER_CHOICES = [(i, i) for i in range(1, 12)]  # Generates choices dynamically

    name = models.CharField(max_length=255, null=False, blank=False)
    category = models.ManyToManyField("Category", blank=True)
    priority = models.IntegerField(
        choices=INTEGER_CHOICES, default=11
    )  # IntegerChoices replaced with IntegerField for choices

    def __str__(self):
        return self.name


class ProductReview(CustomizedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )  # Consider using CASCADE or SET_NULL
    review = models.TextField(null=False, blank=False)  # Ensure review cannot be blank

    def __str__(self):
        return f"Review for {self.product.product_name} - {self.review[:30]}"


class ProductReviewReply(CustomizedModel):
    review = models.ForeignKey(
        ProductReview, on_delete=models.CASCADE, related_name="replies"
    )
    reply = models.TextField(null=False, blank=True)

    def __str__(self):
        return self.review.review
