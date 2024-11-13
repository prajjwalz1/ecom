from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [

    path('checkout',CheckOut.as_view()),
    path('paymentsuccess',eSewaSuccessView.as_view()),
    path('vieworder',order_slip_view),
    path('getsecretkey',order_slip_view),





]
  

