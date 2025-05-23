from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from palikadata.views.distribution_document import DistributionDocumentViewSet
from palikadata.views.distribution_item import DistributionItemViewSet
from palikadata.views.distribution_record import DistributionRecordViewSet
from palikadata.views.local_gov import LocalGovernmentViewSet
from palikadata.views.local_gov_programs import GovernmentProgramViewSet

router = DefaultRouter()
router.register(r"programs", GovernmentProgramViewSet, basename="palika_programs")
router.register(r"govname", LocalGovernmentViewSet, basename="local_gov")
router.register(
    r"distributiondocuments",
    DistributionDocumentViewSet,
    basename="distribution_documents",
)
router.register(
    r"distributionrecords", DistributionRecordViewSet, basename="distribution_records"
)
router.register(
    r"distributionitems", DistributionItemViewSet, basename="distribution_items"
)
urlpatterns = router.urls
