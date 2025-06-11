from datetime import date

from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication as JWT

from palikadata.models.local_government import (  # Adjust import paths as needed
    LocalGovernment,
)
from palikadata.models.palika_karmachari import (
    PalikaKarmachari,  # Add this import if not already present
)
from palikadata.models.palika_program import FiscalYear  # Adjust import paths as needed
from palikadata.models.palika_program import PalikaProgram
from palikadata.permissions.org_staff import IsSamePalikaKarmachari
from palikadata.utils.current_fiscal_year import (
    get_current_bs_year,  # Adjust import paths as needed
)


class PalikaProgramStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSamePalikaKarmachari]
    authentication_classes = [JWT]

    def get_total_budget_allocation(self, palika):

        # Assuming fiscal year starts on Shrawan 1 (mid-July), adjust as per your calendar
        fiscal_year = get_current_bs_year()
        fiscal_year_id = FiscalYear.objects.filter(
            year=fiscal_year,
        ).first()

        total_budget = (
            PalikaProgram.objects.filter(
                local_government=palika,
                fiscal_year=fiscal_year_id,
            )
            .aggregate(total_budget_allocation=models.Sum("program_budget"))
            .get("total_budget_allocation", 0)
            or 0
        )
        return total_budget

    def get(self, request):
        local_government_id = request.query_params.get("local_government")
        """
        Returns overall number of programs, completed programs, and other stats for a given palika.
        Also returns admin user and karyalaya pramukh of the palika.
        """
        try:
            palika = LocalGovernment.objects.get(id=local_government_id)
        except LocalGovernment.DoesNotExist:
            return Response({"detail": "Palika not found."}, status=404)

        programs = PalikaProgram.objects.filter(local_government=palika)
        total_programs = programs.count()
        completed_programs = programs.filter(program_status="completed").count()
        ongoing_programs = programs.filter(program_status="ongoing").count()

        # Get admin user(s)
        admin_karmacharis = PalikaKarmachari.objects.filter(
            palika=palika, is_admin=True, is_active=True
        ).select_related("user")
        admin_user = (
            [
                {
                    "id": karmachari.user.id,
                    "name": f"{karmachari.user.first_name} {karmachari.user.last_name}",
                    "email": karmachari.user.email,
                }
                for karmachari in admin_karmacharis
            ]
            if admin_karmacharis.exists()
            else []
        )

        # Get karyalaya pramukh
        karyalaya_pramukh = (
            PalikaKarmachari.objects.filter(
                palika=palika, is_karyalaya_pramukh=True, is_active=True
            )
            .select_related("user")
            .first()
        )
        karyalaya_pramukh_user = (
            {
                "id": karyalaya_pramukh.user.id,
                "name": f"{karyalaya_pramukh.user.first_name} {karyalaya_pramukh.user.last_name}",
                "email": karyalaya_pramukh.user.email,
            }
            if karyalaya_pramukh
            else None
        )
        budget_allocated = self.get_total_budget_allocation(palika)

        data = {
            "palika": palika.name,
            "total_programs": total_programs,
            "completed_programs": completed_programs,
            "ongoing_programs": ongoing_programs,
            "admin_user": admin_user,
            "karyalaya_pramukh": karyalaya_pramukh_user,
            "budget_allocated": budget_allocated,
        }
        return Response(data)
