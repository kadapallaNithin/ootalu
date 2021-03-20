from django.shortcuts import render,redirect, get_object_or_404, reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, ListView
from django import forms
from .models import PostPaid, WaterPostPaidTransaction, TxnState
from payments.models import Plan, WaterTransaction
from product.models import Product, ProductIPAddress
from product import views as product_views
# from product.views import secure_request
import requests
import secrets
import string
import json
from decimal import Decimal
# if user0 gets key but device is offline. user0 goes. user1 gets same key device is online.
class WaterTransactionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = WaterTransaction
    fields = ['request']
    def get_initial(self):
        initial = super(WaterTransactionCreateView,self).get_initial()
        last_txn = WaterTransaction.objects.filter(plan_id=self.kwargs.get('plan_id')).last()
        if last_txn:
            initial.update({'request':last_txn.request})
        return initial
    def test_func(self):
        plan = get_object_or_404(Plan,id=self.kwargs.get('plan_id'))
        return plan.user == self.request.user
    def form_valid(self,form):
        plan = get_object_or_404(Plan,id=self.kwargs.get('plan_id'))
        form.instance.plan = plan
        #Invalid = False
        if not plan.is_active :
        #    Invalid = True
            messages.warning(self.request,f'Plan is not activated yet! Please contact the owner.')
        elif plan.remaining < form.instance.request:
        #    Invalid = True
            messages.warning(self.request,f'You can only request for { plan.limit } - { plan.used } = { plan.remaining } but requested for { form.instance.request }.')
        elif form.instance.request == 0:
            messages.warning(self.request,f'You are requesting for 0 Units. Request a valid amount.')
        #if Invalid:
        #    return HttpResponseRedirect(reverse('water_transaction',args=(plan.id,)))
        else:
            #self.kwargs['ip_address'] = product_views.get_product_ip(self.request, plan.product_id)
            # # # handled by signals
            # # transactions = WaterTransaction.objects.filter(plan=plan).order_by('id')
            # # if len(transactions) > 0:
            # #     last_transaction = transactions.last()
            # #     refund = last_transaction.request - last_transaction.dispensed
            # #     if refund > 0 :
            # #         plan.used -= refund
            # # plan.used += form.instance.request
            # # plan.save()
            form.instance.key = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
#            form.instance.cash_bytes = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(form.instance.request))
            return super().form_valid(form)
        return HttpResponseRedirect(reverse('water_transaction',args=(plan.id,)))

    def get_context_data(self):
        context = super().get_context_data()
 #       context['plan'] = get_object_or_404(Plan,id=self.kwargs.get('plan_id'))
        context['last_txn'] = WaterTransaction.objects.filter(plan_id=self.kwargs.get('plan_id')).last()
        return context


class WaterTransactionWaitingListView(ListView):
    model = WaterTransaction
    template_name = 'payments/waiting_list.html'
    paginate_by = 10

    def get_queryset(self):
        return WaterTransaction.objects.filter(plan__product_id=self.kwargs.get('product_id'),state=TxnState.in_queue).order_by('started_on')

@login_required
def dispense(request,txn):
    ip = ProductIPAddress.objects.filter(product_id=txn.plan.product.id).last()#order_by('-id')[0]
    key = txn.plan.product.productkey.key
    #key = WaterTransaction.objects.filter(plan__product_id=txn.plan.product.id,state=TxnState.finished).last()
    waiting = WaterTransaction.objects.filter(plan__product_id=txn.plan.product.id,state=TxnState.in_queue)
    if len(waiting) > 0:
        return render(request,'payments/waiting_list.html',context={"object_list":waiting,"txn":txn})
    try:
        # ensure transaction is not cancelled after sending request to MCU.
        prev_state = txn.state
        txn.state = TxnState.running
        txn.save()
        address = "http://"+ip.ip
        url = address+"/turn/"
        data = {"key":key,"req":txn.request,"txn":txn.id,"stop_key":txn.key, "json":1}
        response = requests.post(url, data=data) #,timeout=(5,None)
        print("response content",response.content)
        resp = json.JSONDecoder().decode(response.content.decode())
        if ('req' in resp) and ('txn' in resp) and ('has_dispensed_for' in resp):
            # check req, txn, has_dispensed_for
            return render(request,'payments/finish.html',{"ip":ip.ip,"key":txn.key,"txn":txn})
        elif 'rem' in resp:
            txn.state = prev_state
            txn.save()
            messages.warning(request,"You have to wait. For running transaction, remaining : "+str(resp['rem'])+" units.")
            return render(request,'payments/waiting_list.html',context={"object_list":waiting,"txn":txn})#render(request,'payments/offline.html',{"txn":txn,"waiting":1})
        else:
            txn.state = prev_state
            txn.save()
            messages.warning(request,"There was an error while processing.")
            print(response.content)
            print(data)
        return HttpResponseRedirect(reverse('water_transaction_history'))
    except requests.exceptions.ConnectionError:
        txn.state = prev_state
        txn.save()
        return render(request,'payments/offline.html',{"txn":txn})

@login_required
def stop(request,txn):
    ip = ProductIPAddress.objects.filter(product_id=txn.plan.product.id).last()#order_by('-id')[0]
    try:
        address = "http://"+ip.ip
        url = address+"/finish/"
        data = {"key":txn.key,"txn":txn.id, "json":1}
        response = requests.post(url, data=data)
#        print("response content",response.content)
        resp = json.JSONDecoder().decode(response.content.decode())
        if "finish" in resp:
            if resp["finish"] == -1:
                messages.warning(request, "Already finished!")
            elif resp["finish"] == 4294967295: # counter error
                messages.warning(request, "Please contact us! Please note txnid = "+str(txn.id))
                print("txn is not finished by mcu ",txn.id)
            else:
                # units = resp["finish"]/txn.plan.product.count_per_unit
                units = resp["finish"]
                if units - txn.request > 0:
                    print(units - txn.request)
                messages.success(request, "Dispsensed "+str(units) +" units of water.")
        else:
            messages.warning(request, "The transaction has already finished")# Either or stopped due to power cut.
        return HttpResponseRedirect(reverse('water_transaction_history'))
    except requests.exceptions.ConnectionError:
        messages.warning(request, "Device is offline. Try again when it comes back online.")
    return HttpResponseRedirect(reverse('water_transaction_history'))#render(request,'payments/offline.html',{"txn":txn})

@login_required
def transaction_state_chage(request,to,transaction_id):
    txn = get_object_or_404(WaterTransaction, id=transaction_id)
    if txn.state == TxnState.finished:
        messages.warning(request,f"The transaction with id { txn.id } has already finished or cancelled!")
        return HttpResponseRedirect(reverse('water_transaction_history'))
    user = request.user
    if user.is_authenticated and txn.plan.user == user:
        if to == "dispense":
            return dispense(request,txn)
        elif to == "wait_in_queue":
            return wait_in_queue(request,txn)
        elif to == "stop":
            return stop(request, txn)
        elif to == "cancel":
            return cancel_transaction(request, txn)
    raise Http404("You can't access this transaction!")

@login_required # access via transaction state change
def wait_in_queue(request, txn):
    if txn.state == TxnState.requested:
        txn.state = TxnState.in_queue
        txn.save()
        messages.success(request,f'The transaction with id { txn.id } is put in queue.')
    elif txn.state == TxnState.in_queue:
        messages.warning(request,"The transaction is already in queue")
    elif txn.state == TxnState.running:
        messages.warning(request,"The transaction is already running")
        pass # redirect
    else:
        messages.success(request,"Thank you")
        messages.warning(request,"The transaction finished!")
        return HttpResponseRedirect(reverse('home'))
    return HttpResponseRedirect(reverse('waiting_list',args=(txn.plan.product.id,))) #render(request,'payments/queue.html',{"txn":txn})

@login_required # access via transaction state change
def cancel_transaction(request,txn):
    if txn.state == TxnState.in_queue or txn.state == TxnState.requested:
        txn.state = TxnState.finished
        # txn.dispensed = 0 # it's default
        txn.save()
        messages.success(request,f'The transaction with id { txn.id } is cancelled.')
    else:
        messages.warning(request,f"The transaction with id { txn.id } is under progress. You can't cancel it. But you can stop it.")
    return HttpResponseRedirect(reverse('water_transaction_history'))

def next_txn(product):
    next_txns = WaterTransaction.objects.filter(plan__product_id=product.id,state=TxnState.in_queue).order_by('started_on')
    if len(next_txns) > 0:
        nxt_txn = next_txns.first()
        nxt_txn.state = TxnState.running
        nxt_txn.save()
        return {"code":201,"req":float(nxt_txn.request), "txn":nxt_txn.id,"stop_key":nxt_txn.key} # , "wait":nxt_txn.wait,"dispensed":txn.dispensed,"txn":txn.id
    return dict()

# product side
def store_sensor_values(request):#not currently if implementing, see in finsh_txn_func txn.dispensed == 0 which assumes this is not implemented 
    # txn_id, server_key, prod_id == txn.prod_id 
    return HttpResponse('hi')

def finish_txn_func(g,**kwargs):
    # print(g)
    # if "txn" in g:
    #     print(g["txn"])
    # else:
    #     print("txn not in g")
    if 'txn' in g and 'dispensed' in g:
        txn = get_object_or_404(WaterTransaction,id=g['txn'])
        #if txn.dispensed == 0 : #
        dispensed = Decimal(g['dispensed'])
        error = dispensed - txn.request
        if error < 0.05 and error > 0:
            print(txn.request,dispensed)
            dispensed = txn.request
        txn.dispensed = dispensed
        txn.state = TxnState.finished
        txn.save()
        response = {"code":200}
        response.update(next_txn(txn.plan.product))
        return response
 #       else:
#            return {"code":1,"error":"dispensed was not 0"}
    return {"code":1,"error":"some data missing or unknown error"}

def finish_txn(request):
    return product_views.secure_request(request,finish_txn_func)

def cash(request):
    return HttpResponse('nnnnnnnn')

class WaterTransactionListView(LoginRequiredMixin, ListView):
    model = WaterTransaction
    paginate_by = 10
    def get_queryset(self):
        return WaterTransaction.objects.filter(plan__user=self.request.user).order_by('-started_on')

class PlanCreateView(LoginRequiredMixin,CreateView):
    model = Plan
    fields = ['limit']

    def get_context_data(self):
        context = super().get_context_data()
        context['product'] = get_object_or_404(Product,id=self.kwargs.get('product_id'))
        return context

    def form_valid(self,form):
        user = self.request.user
        if user.is_authenticated:
            form.instance.user = user
            form.instance.product = get_object_or_404(Product,id=self.kwargs.get('product_id'))
#            if len(Plan.objects.filter(user=self.request.user,product=form.instance.product)) == 0:
            try :
                return super().form_valid(form)
            except OverflowError:
                messages.warning(self.request,f'Too big limit!')
        #     else:
        #         messages.warning(self.request,f'Already registered! for { form.instance.product }')
        return redirect('my_plans')

class PlanActivateUpdateView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Plan
    fields = ['limit']
    template_name = 'payments/plan_update.html'
 
    def form_valid(self,form):
        plan = form.instance
        if not plan.is_active :
            plan.is_active = True
            try:
                return super().form_valid(form)
            except OverflowError:
                messages.warning(self.request,f"Too big limit!")
        else:
            messages.warning(self.request,f"You can't activate plan { plan }! as this plan is aleady active.")
        return redirect('my_devices') 

    def test_func(self):
        user = self.request.user
        plan = get_object_or_404(Plan,id=self.kwargs.get('pk'))
        return plan.product.owner == user

class PlanRequestsListView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    model = Plan
    template_name = 'payments/plan_requested_list.html'
    paginate_by = 10
    def get_queryset(self):
        product = get_object_or_404(Product,id=self.kwargs.get('product_id'))
        return Plan.objects.filter(product=product).order_by('-id')

    def test_func(self):
        product = get_object_or_404(Product,id=self.kwargs.get('product_id'))
        return product.owner == self.request.user

class MyPlansListView(LoginRequiredMixin,ListView):
    model = Plan
    paginate_by = 10

    def get_queryset(self):
        return Plan.objects.filter(user=self.request.user).order_by('-date')

class PostPaidCreateView(LoginRequiredMixin, CreateView):
    model = PostPaid#, UserPassesTestMixin
    fields = []#['product']
    def form_valid(self,form):
        form.instance.user = self.request.user
        form.instance.bill = 0
        form.instance.product = get_object_or_404(Product,pk=self.kwargs.get('product_id'))#Product.objects.filter(id=self.kwargs.get('product_id')).first()#request.POST['product']
        if len(PostPaid.objects.filter(user=self.request.user,product=form.instance.product)) != 0:
            messages.warning(self.request,f'Already registered! for { form.instance.product }')
            return redirect('post_paid_list')
        form_is_valid = super().form_valid(form)
        if form_is_valid:
            messages.success(self.request,f'{ form.instance.user } has requested post paid for { form.instance.product }')
        return form_is_valid
        
class PostPaidUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PostPaid
    fields = ['limit']
    def form_valid(self,form):
        form.instance.user = self.request.user
        form.instance.bill = 200
        #form.instance.product = self.request.user.product
        return super().form_valid(form)

class PostPaidListView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    model = PostPaid
    fields = ['product','limit','bill']
    context_object_name = 'object'
    paginate_by = 10

    def get_queryset(self):
        return PostPaid.objects.filter(user=self.request.user)

    def test_func(self):
        user = self.request.user
        if user.is_authenticated:
            #if user.postpaid
            return True
        return False


class WaterPostPaidTransactionCreateView(CreateView):
    model = WaterPostPaidTransaction
    fields = ['num_liters']

def water_dispensed_periodic_not_upto_date(request):
    if request.method == "GET":
        g = request.GET
        if 'key' in g  and '' in g and 'trans' in g :
            prod_ips = ProductIPAddress.objects.filter(product_id=g['prod'])
            if len(prod_ips) >= 1:
                prod_ip = prod_ips.last()
                if prod_ip.server_key == g['key']:
                    prod_key = "nithin"
                    serv_key = "nithinPk"
                    new_prod_ip = ProductIPAddress.objects.create(product_id=g['prod'],ip=g['ip'],product_key=prod_key,server_key=serv_key)
                    new_prod_ip.save()
                    return HttpResponse('{"api_key":"'+prod_key+'","ssid":"kadapalla","password":"12345678"}')
    return HttpResponse("I got nothing")














#class PostPaidForm(LoginRequiredMixin, UserPassesTestMixin, forms.ModelForm):
 #   class Meta:
  #      model = PostPaid
   #     fields = ['product','user']
    
    
#@login_required
#def postpaid(request):
#    if request.method == 'POST':
 #       form = PostPaidForm(request.POST)
  #      if form.is_valid():
   #         form.save()
    #        messages.success(request,f'Postpaid established!')
     #       return redirect('home')
    #else:
     #   form = PostPaidForm()
    #return render(request,'payments/postpaid.html',{'form':form})
