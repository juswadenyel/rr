from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import ReservationForm
from ...models import Reservation
#from utils import supabase_auth_required

#@supabase_auth_required
def reservation_form(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/rr/manage/')
    else:
        form = ReservationForm()
    return render(request, 'rr_app/reservation_form.html', {'form': form})

#@login_required(login_url='/rr/login/')
def reservation_management(request):
    reservations = Reservation.objects.all()
    #reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'rr_app/reservation_management.html', {'reservations': reservations})
