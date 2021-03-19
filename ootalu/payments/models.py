from django.db import models, IntegrityError
from django.urls import reverse
from users.models import User
from product.models import Product, Rate, ProductIPAddress
class Unit(models.Model):
    unit = models.CharField(max_length=16)
    liters_per_unit = models.IntegerField()

    def __str__(self):
        return self.unit

class Plan(models.Model):
    # class Meta:
    #     unique_together = (('user','product'),)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    limit = models.IntegerField(default=0)
    used = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    @property
    def remaining(self):
        return self.limit - self.used
    def get_absolute_url(self):
        return reverse('my_plans')
    def __str__(self):
        return str(self.product)+' '+str(self.user)

class TxnState:
    requested = 0
    in_queue = 1
    running = 2
    finished = 3 # or cancelled

class WaterTransaction(models.Model):
    plan = models.ForeignKey(Plan,on_delete=models.CASCADE)
    dispensed = models.DecimalField(default=0,  max_digits=8, decimal_places=2)#in liters
    request = models.DecimalField(default=0, max_digits=8, decimal_places=2)#in liters
    key = models.CharField(max_length=128) # used to stop txn
    state = models.IntegerField(default=TxnState.requested)
    #wait = models.IntegerField(default=10)
#    cash_bytes = models.TextField(max_length=256)#seems as a complication
    started_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}.[{self.state}] {self.dispensed }/{ self.request }, {self.plan}"

    def get_absolute_url(self):
        return reverse('transaction',args=("dispense",self.id,))
        #"http://"+ProductIPAddress.objects.filter(product_id=self.plan.product_id).last().ip
#         except AttributeError:
#             error = "Sorry there was an error. Could not get IP address of the device. Please take a screenshot and contact us."
# #            messages.warning(request,f'Sorry there was an error. Could not get IP address of device with id { product_id }. Please take a screenshot and contact us.')
#         return reverse('error',args=(error,'water_transaction_history',))#kwargs={"redirect":"my_plans","error":error})#"http://"+a
class PostPaid(models.Model):
    class Meta:
        unique_together = (('user','product'),)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    limit = models.IntegerField(default=0)
    bill = models.DecimalField(default=0,max_digits=10,decimal_places=2)

    def __str__(self):
        return f'{ self.user } - { self.product }'
    def get_absolute_url(self):
        return reverse('products-rates-list',kwargs={'pk':self.product.id})#('product-detail',kwargs={'pk':self.pk})

'''class WaterPrepaidTransaction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)'''

class WaterPostPaidTransaction(models.Model):
    post_paid = models.ForeignKey(PostPaid,on_delete=models.CASCADE)
    rate = models.ForeignKey(Rate,on_delete=models.CASCADE)#make sure rate.product == post_paid.product
    units = models.ForeignKey(Unit,on_delete=models.SET_NULL,null=True)
    num_units = models.DecimalField(max_digits=10,decimal_places=3,default=0)
    cash = models.DecimalField(max_digits=10,decimal_places=3,default=0)
    started_on = models.DateTimeField(auto_now=True)

class WaterDispensedPeriodic(models.Model):
    transation = models.ForeignKey(WaterPostPaidTransaction,on_delete=models.CASCADE)
    module_at = models.IntegerField()
    count = models.IntegerField()

class WaterDispenseFinish(models.Model):
    transation = models.ForeignKey(WaterPostPaidTransaction,on_delete=models.CASCADE)
    refund = models.DecimalField(max_digits=10,decimal_places=3,default=0)
    finished_on = models.DateTimeField(auto_now=True)
    num_liters = models.DecimalField(max_digits=10,decimal_places=3,default=0)