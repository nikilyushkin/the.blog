from django.contrib.auth import logout
from django.shortcuts import render, redirect


def log_in(request):
    return render(request, "users/login.html")


def log_out(request):
    logout(request)
    return redirect("index")
