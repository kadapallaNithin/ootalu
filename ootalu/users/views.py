from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserSignupForm, UserUpdateForm,ProfileUpdateForm
# Create your views here.
def signup(request):
    if request.method == 'POST' :
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'An account created for { username }!')
            return redirect('login')
    else:
        form = UserSignupForm()
    return render(request,'users/signup.html',{'form':form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST,instance=request.user)
        profile_instance = request.user.profile
        if 'remove_pic' in request.POST and request.POST['remove_pic'] == "on"  :
            profile_instance.pic = "default.png"

        p_form = ProfileUpdateForm(request.POST,
                                    request.FILES,
                                    instance=profile_instance)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,"Your account has been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request,'users/profile.html',{'u_form':u_form,'p_form':p_form})