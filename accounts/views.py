from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, get_user_model, login, logout
from .forms import UserLoginForm, UserRegisterForm

#handels the basic login view
def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        #redirects to the page where the login the 'sign in' was chosen from
        if next:
            return redirect(next)
        #otherwise to the main 'home' page
        return redirect('/')

    context = {
        'form': form
    }
    return render(request, "accounts/login.html", context)


def register_view(request):
    next = request.GET.get('next')
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        #to authenticate a user, it's required to set the new password first and save it
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect('/')

    context = {
        'form': form,
    }
    return render(request, "accounts/register.html", context)


def logout_view(request):
    logout(request)
    return redirect('/')
