import requests
from django.contrib.auth import authenticate, login, logout
from django.http import response
from django.http import request
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from .forms import CreateUserForm
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from django.contrib.auth import authenticate, login

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('username')
            form.save()
            messages.success(request, "Account was created for "+user)
            return redirect('home')


    context ={'form': form}
    return render(request, 'accounts/register.html', context=context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(request.path)
            return redirect('home')
        else:
            messages.info(request, "Username or password is incorrect")

    return redirect('home')

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('login')


## discord login
auth_url_discord = ''

def discord_login(request: HttpRequest):
    return redirect(auth_url_discord)

def discord_login_redirect(request: HttpRequest):
    code = request.GET.get("code")
    user = exchange_code(code)
    discord_user = authenticate(request, user=user)
    discord_user = list(discord_user).pop()
    if user is not None:
        login(request, discord_user, backend='accounts.auth.DiscordAuthenticationBackend')
        return redirect('home')
    else:
        messages.info(request, "Username or password is incorrect")
    return JsonResponse({"status": False})

def exchange_code(code: str):
    data = {
        "client_id": "",
        "client_secret": "",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:8000/oauth2/login/redirect",
        "scope": "identify"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    credentials = response.json()
    access_token = credentials['access_token']
    response = requests.get("https://discord.com/api/v6/users/@me", headers={
        'Authorization': 'Bearer %s' % access_token
    })

    user = response.json()
    return user
## discord login