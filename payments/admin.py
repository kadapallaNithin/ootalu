from django.contrib import admin
from .models import Plan, PostPaid, WaterPostPaidTransaction, WaterDispensedPeriodic, WaterTransaction#, WaterDispensedFinish
admin.site.register(Plan)
admin.site.register(PostPaid)
admin.site.register(WaterTransaction)
admin.site.register(WaterPostPaidTransaction)
admin.site.register(WaterDispensedPeriodic)
#admin.site.register(WaterDispensedFinish)