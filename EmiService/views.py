from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializers import EMIConfigSerializer, LoanTypeSerializer


# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import LoanType, LoanTenure, EMIConfig

from decimal import Decimal

def calculate_emi(request):
    """
    Calculate the EMI for a given loan type, tenure, and loan amount.
    """
    # Extract parameters from request (query parameters or POST data)
    loan_type_id = request.GET.get('loan_type_id')
    tenure_months = int(request.GET.get('tenure_months'))
    principal = float(request.GET.get('principal'))  # Loan amount (Principal)
    pay_amount=Decimal(request.GET.get('pay_amount'))
    
    # Convert principal to Decimal
    principal = Decimal(principal)-pay_amount

    # Validate inputs
    if not loan_type_id or not tenure_months or not principal:
        return JsonResponse({"success":False,"error": "Missing required parameters"}, status=400)

    # Fetch loan type and associated EMI config
    loan_type = get_object_or_404(LoanType, id=loan_type_id)
    
    # Check if tenure is valid for the selected loan type
    valid_tenure = LoanTenure.objects.filter(loan_type=loan_type, months=tenure_months).exists()
    if not valid_tenure:
        return JsonResponse({"success":False,"error": f"Invalid tenure {tenure_months} months for the selected loan type."}, status=400)

    # Fetch the EMIConfig for this loan type and tenure
    try:
        emi_config = EMIConfig.objects.get(loan_type=loan_type, tenure_months=tenure_months)
        interest_rate = emi_config.interest_rate
    except EMIConfig.DoesNotExist:
        return JsonResponse({"success":False,"error": f"EMI configuration not found for the selected loan type and tenure."}, status=400)

    # Convert interest rate to monthly rate and handle as Decimal
    monthly_interest_rate = Decimal(interest_rate) / Decimal(100) / Decimal(12)

    # Calculate the EMI
    if monthly_interest_rate == 0:  # Handle case where interest rate is 0%
        emi = principal / Decimal(tenure_months)  # No interest case
    else:
        emi = (principal * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure_months) / ((1 + monthly_interest_rate) ** tenure_months - Decimal(1))

    # Return the calculated EMI as a response
    return JsonResponse({
        "success":True,
        "emi": round(emi, 2),
        "loan_type": loan_type.name,
        "tenure_months": tenure_months,
        "principal": float(principal),  # Convert back to float for response
        "interest_rate": float(interest_rate)  # Convert back to float for response
    })



class EMIConfigListCreateView(ListCreateAPIView):
    """
    API for listing and creating EMI configurations.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = EMIConfig.objects.all()
    serializer_class = EMIConfigSerializer
    pagination_class = PageNumberPagination


class EMIConfigDetailView(RetrieveUpdateDestroyAPIView):
    """
    API for retrieving, updating, and deleting a specific EMI configuration.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = EMIConfig.objects.all()
    serializer_class = EMIConfigSerializer


class LoanTypeListCreateView(ListCreateAPIView):
    """
    API for listing and creating loan types.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
    pagination_class = PageNumberPagination


class LoanTypeDetailView(RetrieveUpdateDestroyAPIView):
    """
    API for retrieving, updating, and deleting a specific loan type.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
