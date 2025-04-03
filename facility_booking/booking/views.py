from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Room, Booking
from .forms import BookingForm, BookingUpdateForm
from django.utils import timezone
import random

def room_list(request):
    # Search/filter functionality using GET parameters (e.g., by capacity or keyword in equipment)
    query = request.GET.get('q', '')
    rooms = Room.objects.all()
    if query:
        rooms = rooms.filter(name__icontains=query) | rooms.filter(equipment__icontains=query)
    return render(request, 'booking/room_list.html', {'rooms': rooms, 'query': query})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    all_other_rooms = list(Room.objects.exclude(pk=pk))  
    random.shuffle(all_other_rooms)
    other_rooms = all_other_rooms[:8]
    bookings = Booking.objects.filter(room=room).order_by('start_time')
    return render(request, 'booking/room_detail.html', {'room': room, 'bookings': bookings, 'other_rooms': other_rooms})

@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Booking request submitted successfully. An email notification has been sent.')
            # Send a dummy email notification (prints to console)
            send_mail(
                'Booking Request Submitted',
                f'Your booking for {booking.event_title} is now pending approval.',
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                [request.user.email],
                fail_silently=True,
            )
            return redirect('booking_success')
    else:
        form = BookingForm()
    return render(request, 'booking/booking_form.html', {'form': form})

@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status not in ['pending', 'approved']:
        messages.error(request, "Only pending or approved bookings can be updated.")
        return redirect('my_bookings')

    if request.method == 'POST':
        form = BookingUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully.')
            return redirect('my_bookings')
    else:
        form = BookingUpdateForm(instance=booking)
    return render(request, 'booking/booking_update.html', {'form': form, 'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status in ['cancelled']:
        messages.error(request, "Booking is already cancelled.")
    else:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
    return redirect('my_bookings')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

# Simple admin view for pending bookings and approval actions.
@user_passes_test(lambda u: u.is_staff)
def pending_bookings(request):
    bookings = Booking.objects.filter(status='pending').order_by('start_time')
    return render(request, 'booking/pending_bookings.html', {'bookings': bookings})

@user_passes_test(lambda u: u.is_staff)
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = 'approved'
    booking.save()
    messages.success(request, f"Booking '{booking.event_title}' approved.")
    # Send notification email
    send_mail(
        'Booking Approved',
        f'Your booking for {booking.event_title} has been approved.',
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        [booking.user.email],
        fail_silently=True,
    )
    return redirect('pending_bookings')

@user_passes_test(lambda u: u.is_staff)
def deny_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = 'denied'
    booking.save()
    messages.success(request, f"Booking '{booking.event_title}' denied.")
    # Send notification email
    send_mail(
        'Booking Denied',
        f'Your booking for {booking.event_title} has been denied.',
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        [booking.user.email],
        fail_silently=True,
    )
    return redirect('pending_bookings')

# A simple calendar view that lists upcoming bookings.
def calendar_view(request):
    today = timezone.now()
    bookings = Booking.objects.filter(start_time__gte=today, status__in=['approved', 'pending']).order_by('start_time')
    return render(request, 'booking/calendar.html', {'bookings': bookings})

def booking_success(request):
    return render(request, 'booking/booking_success.html')
