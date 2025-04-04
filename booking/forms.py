from django import forms
from django.core.exceptions import ValidationError
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'event_title', 'event_date', 'start_time', 'end_time']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-select'}),
            'event_title': forms.TextInput(attrs={'class': 'form-control'}),
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        event_date = cleaned_data.get('event_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("End time must be after start time.")

            # Check for booking conflicts on the same event date
            overlapping = Booking.objects.filter(
                room=room,
                event_date=event_date,
                status__in=['pending', 'approved'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if overlapping.exists():
                raise ValidationError("This room is already booked during the selected time.")
        return cleaned_data
    
class BookingUpdateForm(BookingForm):
    # Same as BookingForm, can be extended for additional update-specific logic.
    pass
