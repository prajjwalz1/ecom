from rest_framework.permissions import BasePermission

from palikadata.models.palika_karmachari import PalikaKarmachari


class IsSamePalikaKarmachari(BasePermission):
    """
    Allow access if user is a karmachari and belongs to the same palika as the object.
    """

    def has_object_permission(self, request, view, obj):
        try:
            user_a_karmachari = PalikaKarmachari.objects.get(
                user=request.user, is_active=True
            )
        except PalikaKarmachari.DoesNotExist:
            return False
        if hasattr(obj, "palika"):
            return obj.palika == user_a_karmachari.palika
        elif hasattr(obj, "organization"):
            return obj.organization == user_a_karmachari.palika
        elif hasattr(obj, "local_government"):
            return obj.local_government == user_a_karmachari.palika
        elif hasattr(obj, "karmachari") and hasattr(obj.karmachari, "palika"):
            return obj.karmachari.palika == user_a_karmachari.palika
        return False

    def has_permission(self, request, view):
        local_gov = request.GET.get("local_government", None)
        return PalikaKarmachari.objects.filter(
            user=request.user, is_active=True, palika=local_gov
        ).exists()
