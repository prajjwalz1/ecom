from django.db import models
from .mixins import CustomizedModel
from ckeditor.fields import RichTextField

# Create your models here.
import logging
logger = logging.getLogger(__name__)

class Category(CustomizedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories'
    )

    def __str__(self):
        return self.name

# Brand Model
class Brand(CustomizedModel):
    name = models.CharField(max_length=255)
    image=models.ImageField(upload_to="Brands",null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Tag Model
class Tag(CustomizedModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name



class Specification(CustomizedModel):
    spec_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"{self.spec_name} "

class Product(CustomizedModel):
    product_name=models.CharField(max_length=255,null=False,blank=True)
    product_description=models.TextField(null=False,blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    details= RichTextField(null=True,blank=True) 

    def __str__(self) -> str:
        return self.product_name
    
    def save(self, *args, **kwargs):
        logger.info(f"Saving Product: {self.product_name} with description: {self.product_description}")
        super().save(*args, **kwargs)


class ProductImage(CustomizedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'Image for {self.product.product_name}'
    

class ProductSpecification(CustomizedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    spec_name=models.ForeignKey(Specification,on_delete=models.CASCADE)
    value=models.CharField(max_length=255,null=True,blank=True)
    value_unit=models.CharField(max_length=255,null=True,blank=True)
    
    
    def __str__(self) -> str:
        return f"{self.product.product_name} - {self.spec_name.spec_name}: {self.value}"




class CarouselImage(CustomizedModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='carousel_images/')
    order = models.PositiveIntegerField(default=0)  # To maintain the order of images
    is_active = models.BooleanField(default=True)  # Whether the image is currently active in the carousel
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']  # Order by the 'order' field in ascending order

    def __str__(self):
        return self.title or f"Carousel Image {self.id}"
    

class Navbar(CustomizedModel):
    name=models.CharField(max_length=255,null=False,blank=False)
    category=models.ManyToManyField(Category,blank=True)

    def __str__(Self):
        return Self.name