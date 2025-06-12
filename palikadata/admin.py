from django.contrib import admin

from palikadata.models.local_government import LocalGovernment
from palikadata.models.palika_karmachari import PalikaKarmachari
from palikadata.models.palika_program import (
    FiscalYear,
    PalikaProgram,
    PalikaProgramDocument,
)
from palikadata.models.palika_saakha import PalikaSakha
from palikadata.models.record import *
from palikadata.models.residents import LocalResident
from palikadata.models.ward import Ward

# Register your models here.
admin.site.register(LocalGovernment)
admin.site.register(PalikaProgram)
admin.site.register(DistributionDocument)
admin.site.register(DistributionItem)
admin.site.register(Records)
admin.site.register(LocalResident)
admin.site.register(Ward)
admin.site.register(PalikaSakha)
admin.site.register(PalikaKarmachari)
admin.site.register(FiscalYear)
admin.site.register(PalikaProgramDocument)
