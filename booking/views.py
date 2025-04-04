from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Room, Booking, Equipment
from .forms import BookingForm, BookingUpdateForm, DocumentForm, UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
import random

def room_list(request):
    rooms = Room.objects.all()
    equipment_list = Equipment.objects.all()

    # Retrieve filter parameters from GET
    event_date = request.GET.get('event_date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    capacity = request.GET.get('capacity')
    selected_equipment = request.GET.getlist('equipment')
    query = request.GET.get('q', '')

    # Filter by date and time if provided
    if event_date and start_time and end_time:
        # Exclude rooms that have a booking on that date overlapping with the given times
        rooms = rooms.exclude(
            booking__event_date=event_date,
            booking__start_time__lt=end_time,
            booking__end_time__gt=start_time,
            booking__status__in=['pending', 'approved']
        )
    
    # Filter by equipment if provided (rooms must have all selected equipment items)
    if selected_equipment:
        for eq_id in selected_equipment:
            rooms = rooms.filter(equipment=eq_id)
    
    # Optionally, filter by room name or description with a query string
    if query:
        rooms = rooms.filter(name__icontains=query)

    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)

    return render(request, 'booking/room_list.html', {
        'rooms': rooms,
        'equipment_list': equipment_list,
        'query': query,
        'event_date': event_date or '',
        'start_time': start_time or '',
        'end_time': end_time or '',
        'capacity': capacity or '',
        'selected_equipment': selected_equipment,
    })


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    all_other_rooms = list(Room.objects.exclude(pk=pk))  
    random.shuffle(all_other_rooms)
    other_rooms = all_other_rooms[:8]
    bookings = Booking.objects.filter(room=room).order_by('event_date', 'start_time')

    # Pre-fill the booking form with date and time from GET (if available)
    initial_data = {'room': room.id}
    if 'event_date' in request.GET:
        initial_data['event_date'] = request.GET.get('event_date')
    if 'start_time' in request.GET:
        initial_data['start_time'] = request.GET.get('start_time')
    if 'end_time' in request.GET:
        initial_data['end_time'] = request.GET.get('end_time')

    booking_form = BookingForm(initial=initial_data)

    # Check if open_modal flag is present
    open_modal = request.GET.get('open_modal', 'false').lower() == 'true'

    return render(request, 'booking/room_detail.html', {
        'room': room,
        'bookings': bookings,
        'other_rooms': other_rooms,
        'form': booking_form,
        'open_modal': open_modal,
    })

@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Booking request submitted successfully.')
            send_mail(
                'Booking Request Submitted',
                f'Your booking for {booking.event_title} on {booking.event_date} is now pending approval.',
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                [request.user.email],
                fail_silently=True,
            )
            return redirect('booking_success')
        else:
            messages.error(request, "There was an error with your booking submission.")
    # Optionally, redirect back to room_detail if not POST.
    return redirect(request.META.get('HTTP_REFERER', '/'))

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

@login_required
def profile(request):
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in your profile information.")
            password_form = PasswordChangeForm(user)  # Empty form for display
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in the password form.")
            profile_form = UserProfileForm(instance=user)
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'booking/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'bookings': bookings,
        'user': user,
    })

def how_to_book(request):
    # A blank page for now (you can fill it with instructions later)
    return render(request, 'booking/how_to_book.html')

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('document_upload')
        else:
            messages.error(request, "Error uploading document.")
    else:
        form = DocumentForm()
    # A simple checklist (you can add more items as needed)
    checklist = [
        "Signed booking form",
        "Proof of identity",
        "Event permit (if applicable)",
    ]
    return render(request, 'booking/document_upload.html', {'form': form, 'checklist': checklist})

# A simple calendar view that lists upcoming bookings.
def calendar_view(request):
    today = timezone.now()
    bookings = Booking.objects.filter(event_date__gte=today, status__in=['approved', 'pending']).order_by('event_date')
    return render(request, 'booking/calendar.html', {'bookings': bookings})

def booking_success(request):
    return render(request, 'booking/booking_success.html')
