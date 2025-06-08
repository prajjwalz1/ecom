from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from palikadata.models.palika_saakha import PalikaSakha, PalikaSakhaPramukhHistory


@receiver(pre_save, sender=PalikaSakha)
def update_pramukh_history(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object, no history yet

    old_instance = PalikaSakha.objects.get(pk=instance.pk)
    if old_instance.sakha_pramukh != instance.sakha_pramukh:
        # End previous chief's tenure
        PalikaSakhaPramukhHistory.objects.filter(
            palika_sakha=instance, tenure_to__isnull=True
        ).update(tenure_to=timezone.now().date())


@receiver(post_save, sender=PalikaSakha)
def create_pramukh_history(sender, instance, created, **kwargs):
    if created or not instance.sakha_pramukh:
        return
    # Check if a history record already exists for this chief and branch with open tenure
    exists = PalikaSakhaPramukhHistory.objects.filter(
        palika_sakha=instance,
        sakha_pramukh=instance.sakha_pramukh,
        tenure_to__isnull=True,
    ).exists()
    if not exists:
        PalikaSakhaPramukhHistory.objects.create(
            palika_sakha=instance,
            sakha_pramukh=instance.sakha_pramukh,
            tenure_from=timezone.now().date(),
            tenure_to=None,
        )
