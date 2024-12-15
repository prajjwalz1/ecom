from django.contrib import admin
from .models import EMIConfig, LoanType, LoanTenure

# Registering LoanType in the Django admin with customization
@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('name', 'default_interest_rate', 'max_tenure_years', 'description')
    
    # Adding filters for easy searching
    list_filter = ('default_interest_rate', 'max_tenure_years', 'name')
    
    # Adding search fields to search through name and interest rate
    search_fields = ('name', 'default_interest_rate')
    
    # Adding ordering to default view
    ordering = ('-default_interest_rate',)
    
    # Displaying how the model should appear when editing an instance
    fieldsets = (
        (None, {
            'fields': ('name', 'default_interest_rate', 'max_tenure_years', 'description')
        }),
    )

# Registering LoanTenure in the Django admin
@admin.register(LoanTenure)
class LoanTenureAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('loan_type', 'months')
    
    # Adding filters for easy searching
    list_filter = ('loan_type',)
    
    # Adding search fields to search through loan type name
    search_fields = ('loan_type__name',)
    
    # Displaying how the model should appear when editing an instance
    fieldsets = (
        (None, {
            'fields': ('loan_type', 'months')
        }),
    )
    
    # Optional: Enforce uniqueness of loan_type and months using admin validation
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('loan_type', 'months')


# Registering EMIConfig in the Django admin
@admin.register(EMIConfig)
class EMIConfigAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('loan_type', 'interest_rate', 'tenure_months')
    
    # Adding filters for easy searching
    list_filter = ('loan_type', 'interest_rate', 'tenure_months')
    
    # Adding search fields to search through loan type name and interest rate
    search_fields = ('loan_type__name', 'interest_rate')
    
    # Displaying how the model should appear when editing an instance
    fieldsets = (
        (None, {
            'fields': ('loan_type', 'interest_rate', 'tenure_months')
        }),
    )

    # Override save method to trigger validation of EMIConfig model
    def save_model(self, request, obj, form, change):
        obj.clean()  # Ensuring validation is triggered
        super().save_model(request, obj, form, change)

    # Optional: Show only active EMIConfig entries by default
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.all()  # You can add a filter for 'is_active' if needed

