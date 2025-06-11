from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from palikadata.views.dashboard import PalikaProgramStatsAPIView
from palikadata.views.distribution_document import DistributionDocumentViewSet
from palikadata.views.distribution_item import DistributionItemViewSet
from palikadata.views.distribution_record import DistributionRecordViewSet
from palikadata.views.local_gov import LocalGovernmentViewSet
from palikadata.views.local_gov_programs import (
    GovernmentProgramAPIView,
    ProgramApprovalAPIView,
    ProgramDocumentView,
)
from palikadata.views.palika_karmachari import PalikaKarmachariAPIView
from palikadata.views.sakha import PalikaSakhaViewSet

router = DefaultRouter()
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
router.register(r"palika-sakha", PalikaSakhaViewSet)

urlpatterns = [
    # Add any custom paths here, for example:
    path(
        "programdocuments/",
        ProgramDocumentView.as_view(),
        name="custom_view",
    ),
    path("programaprroval", ProgramApprovalAPIView.as_view(), name="program_approval"),
    path(
        "programs",
        GovernmentProgramAPIView.as_view(),
        name="palika_programs",
    ),
    path(
        "dashboard",
        PalikaProgramStatsAPIView.as_view(),
        name="dashboard",
    ),
    path("karmachari/", PalikaKarmachariAPIView.as_view()),  # POST to add
    path("karmachari/<int:pk>/", PalikaKarmachariAPIView.as_view()),  # PUT to update
]


urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
