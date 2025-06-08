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
        if karmachari_sakha_details:
            sakha = karmachari_sakha_details.sakha.first()
            palika_sakha_id = sakha.id if sakha else None
            return {
                "palika_sakha_id": palika_sakha_id,
                "user_id": user.id,
                "palika_id": karmachari_sakha_details.palika.id,
                "karmachari_id": karmachari_sakha_details.id,
            }

        return None
