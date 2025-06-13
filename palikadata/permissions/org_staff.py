from rest_framework.permissions import BasePermission

from palikadata.models.palika_karmachari import PalikaKarmachari


class IsSamePalikaKarmachari(BasePermission):
    """
    Allow access if user is a karmachari and belongs to the same palika as the object.
    """

    def has_object_permission(self, request, view, obj):
        local_gov = request.GET.get("local_government")
        if not local_gov:
            return False

        user_karmachari = PalikaKarmachari.objects.filter(
            user=request.user, is_active=True, palika_id=local_gov
        ).first()

        if not user_karmachari:
            return False

        user_palika = user_karmachari.palika

        if hasattr(obj, "palika"):
            print("1")
            return obj.palika == user_palika

        if hasattr(obj, "organization"):
            print("2")
            return obj.organization == user_palika

        if hasattr(obj, "local_government"):
            print("3")
            return obj.local_government == user_palika

        if hasattr(obj, "karmachari") and hasattr(obj.karmachari, "palika"):
            print("4")
            return obj.karmachari.palika == user_palika

        if getattr(user_karmachari, "is_admin", False):
            return True

        return False

    def has_permission(self, request, view):
        local_gov = request.GET.get("local_government", None)
        return PalikaKarmachari.objects.filter(
            user=request.user, is_active=True, palika_id=local_gov
        ).exists()


class IsPalikaAdmin(BasePermission):
    """
    Allow access only if user is a palika admin.
    """

    def has_permission(self, request, view=None):
        return PalikaKarmachari.objects.filter(
            user=request.user,
            is_active=True,
            is_admin=True,
            palika=request.GET.get("local_government", None),
        ).exists()
