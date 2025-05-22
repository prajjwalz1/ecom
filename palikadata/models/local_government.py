from product.mixins import *


class LocalGovernment(CustomizedModel):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    code = models.CharField(max_length=255, null=False, blank=False, unique=True)
    logo = models.ImageField(upload_to="localgovernment/logo", null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name if self.name else str(None)
