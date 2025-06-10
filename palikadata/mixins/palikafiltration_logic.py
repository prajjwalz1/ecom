class OrgDeptQuerysetMixin:

    def get_filtered_queryset(self, queryset):
        user = self.request.user
        karmachari_details = user.karmachari_details.all()

        for karmachari_detail in karmachari_details:
            user_palika = karmachari_detail.palika
            sakha = karmachari_detail.palika_sakha

            if user_palika and sakha:
                return queryset.filter(organization=user_palika, department=sakha)

        return queryset.none()
