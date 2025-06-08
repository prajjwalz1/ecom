from django.contrib import admin

from palikadata.models.distribution import *
from palikadata.models.distribution import (
    DistributionDocument,
    DistributionItem,
    DistributionRecord,
)
from palikadata.models.local_government import LocalGovernment
from palikadata.models.palika_karmachari import PalikaKarmachari
from palikadata.models.palika_program import PalikaProgram
from palikadata.models.palika_saakha import PalikaSakha
from palikadata.models.residents import LocalResident
from palikadata.models.ward import Ward

# Register your models here.
admin.site.register(LocalGovernment)
admin.site.register(PalikaProgram)
admin.site.register(DistributionDocument)
admin.site.register(DistributionItem)
admin.site.register(DistributionRecord)
admin.site.register(LocalResident)
admin.site.register(Ward)
admin.site.register(PalikaSakha)
admin.site.register(PalikaKarmachari)
