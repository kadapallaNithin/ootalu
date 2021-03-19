from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductIPAddress, ServerKey, ProductKey
from payments.models import WaterTransaction, Plan, TxnState
import secrets
import string
@receiver(post_save,sender=Product)
def create_product_ip_address(sender,instance,created,**kwargs):
    if created:
        ProductIPAddress.objects.create(product=instance,ip="127.0.0.1")
        sk = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
        ServerKey.objects.create(product=instance,key=sk)
        pk = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
        ck = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
        ProductKey.objects.create(product=instance, key=pk, config_key=ck)
        plan = Plan.objects.create(product=instance,user_id=1,limit=0,used=0)
        stop_key = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
        WaterTransaction.objects.create(plan=plan,dispensed=0,request=0,key=stop_key,state=TxnState.finished)

# @receiver(post_save,sender=ServerKey)
# def create_server_key(sender,instance,created,**kwargs):
#     if created:
#         if instance.key == "nithinSK":
#             instance.key = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))

# @receiver(post_save,sender=ProductKey)
# def create_product_key(sender,instance,created,**kwargs):
#     if created:
#         if instance.key == "nithinPK":
#             instance.key = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))