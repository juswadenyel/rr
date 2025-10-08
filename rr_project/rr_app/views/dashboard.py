from django.shortcuts import render

def dashboard_render(request):
    return render(request, 'rr_app/dashboard.html')