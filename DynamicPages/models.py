from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
from django.db import models

class DynamicPage(models.Model):
    """
    Model to store dynamic HTML content for rendering pages.
    """
    title = models.CharField(max_length=255, unique=True, help_text="Title of the page.")
    slug = models.SlugField(max_length=255, unique=True, help_text="Slug for the page URL.")
    content= RichTextField(null=True,blank=True) 
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the page was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the page was last updated.")

    def __str__(self):
        return self.title
