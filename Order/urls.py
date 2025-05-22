from django.contrib import admin
from django.urls import include, path

from .views import *

urlpatterns = [
    path("checkout", CheckOut.as_view()),
    path("paymentsuccess", eSewaSuccessView.as_view()),
    path("vieworder", order_slip_view),
    path("getsecretkey", secretkey),
    path("uploadpaymentslip", UploadPaymentProofView.as_view()),
    path("validatepromocode", Promocode.as_view()),
    path("promocode", PromocodeListCreateView.as_view()),
    path("promocode/<int:pk>/", PromocodeRetrieveUpdateDestroyView.as_view()),
    path("", OrderListCreateView.as_view()),
    path("<int:pk>/", OrderRetrieveUpdateDestroyView.as_view()),
    path(
        "order-insights/monthly/",
        MonthlyOrderInsightsAPIView.as_view(),
        name="monthly-order-insights",
    ),
]
