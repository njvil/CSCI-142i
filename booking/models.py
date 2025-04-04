from django.db import models
from django.contrib.auth.models import User

class Equipment(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    capacity = models.IntegerField()
    location = models.CharField(max_length=100)
    # Change equipment to a ManyToMany field
    equipment = models.ManyToManyField(Equipment, blank=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('n/a', 'Not Applicable'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    event_title = models.CharField(max_length=200)
    # Assume the event is on one day; separate date, start, and end times.
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='n/a')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_title} - {self.room.name}"

    class Meta:
        ordering = ['-event_date', '-start_time']
