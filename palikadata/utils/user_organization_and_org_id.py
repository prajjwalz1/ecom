from palikadata.models.palika_program import FiscalYear
from palikadata.utils.current_fiscal_year import get_current_bs_year


class GetUserOrganizationAndOrgId:
    """
    This class provides methods to get the organization ID and user ID
    based on the request object.
    """

    @staticmethod
    def get_user_organization_id(user):
        """
        Returns the organization ID of the user from the request object.
        """
        karmachari_sakha_details = user.karmachari_details.first()
        fiscal_year = FiscalYear.objects.filter(is_current=True).first()
        if karmachari_sakha_details:
            sakha = karmachari_sakha_details.sakha.first()
            palika_sakha_id = sakha.id if sakha else None

            return {
                "palika_sakha_id": palika_sakha_id,
                "user_id": user.id,
                "palika_id": karmachari_sakha_details.palika.id,
                "karmachari_id": karmachari_sakha_details.id,
                "fiscal_year": fiscal_year.year,
                "fiscal_year_id": fiscal_year.id,
                "is_organization_admin": karmachari_sakha_details.is_admin,
            }

        return None
