from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Plan, WaterTransaction, TxnState

@receiver(pre_save,sender=WaterTransaction)
def plan_used_update(sender,instance,**kwargs):
    if instance.id and instance.state == TxnState.finished:
        # old = WaterTransaction.objects.get(id=instance.id)
        # if old.not_finished:
            plan = Plan.objects.get(id=instance.plan.id)
            plan.used -= instance.request - instance.dispensed
            # print(plan.used,instance.request,instance.dispensed)
            # instance.not_finished = False
            plan.save()

@receiver(post_save,sender=WaterTransaction)
def plan_used_update_create(sender,instance,created,**kwargs):
    if created:
        plan = Plan.objects.get(id=instance.plan.id)
        plan.used += instance.request
        plan.save()
    