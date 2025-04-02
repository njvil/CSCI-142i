import os
import django
import datetime
from django.utils import timezone

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "facility_booking.settings")
django.setup()

from django.contrib.auth.models import User
from booking.models import Room, Booking

# Create test users
users_data = [
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe"
    },
    {
        "username": "jane_doe",
        "email": "jane@example.com",
        "password": "password123",
        "first_name": "Jane",
        "last_name": "Doe"
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpassword",
        "first_name": "Admin",
        "last_name": "User"
    },
]

for udata in users_data:
    if not User.objects.filter(username=udata["username"]).exists():
        user = User.objects.create_user(
            username=udata["username"],
            email=udata["email"],
            password=udata["password"],
            first_name=udata["first_name"],
            last_name=udata["last_name"]
        )
        print(f"Created user: {user.username}")
    else:
        print(f"User {udata['username']} already exists.")

# Create dummy rooms
rooms_data = [
    {
        "name": "Ateneo Main Hall",
        "description": "Spacious hall for major events.",
        "capacity": 500,
        "location": "Main Building",
        "equipment": "Sound system, Projector"
    },
    {
        "name": "Ateneo Room 101",
        "description": "Ideal for small meetings and study sessions.",
        "capacity": 30,
        "location": "Building A, Floor 1",
        "equipment": "Whiteboard, TV"
    },
    {
        "name": "Ateneo Conference Room",
        "description": "Professional setting for conferences and seminars.",
        "capacity": 100,
        "location": "Building B, Floor 2",
        "equipment": "Projector, Conference Phone"
    },
    {
        "name": "Ateneo Rehearsal Space",
        "description": "Acoustic-friendly space for rehearsals.",
        "capacity": 50,
        "location": "Building C, Basement",
        "equipment": "Sound system, Mirrors"
    },
    {
        "name": "Ateneo Auditorium",
        "description": "Large auditorium for presentations and performances.",
        "capacity": 300,
        "location": "Main Auditorium",
        "equipment": "Stage, Lighting, Sound system"
    },
]

for rdata in rooms_data:
    room, created = Room.objects.get_or_create(
        name=rdata["name"],
        defaults=rdata,
    )
    if created:
        print(f"Created room: {room.name}")
    else:
        print(f"Room {room.name} already exists.")

# Optionally, create a dummy booking
try:
    john = User.objects.get(username="john_doe")
    room_101 = Room.objects.get(name="Ateneo Room 101")
    start_time = timezone.now() + datetime.timedelta(days=1)
    end_time = start_time + datetime.timedelta(hours=2)
    booking, created = Booking.objects.get_or_create(
        user=john,
        room=room_101,
        event_title="Team Meeting",
        start_time=start_time,
        end_time=end_time,
        defaults={"status": "approved"}
    )
    if created:
        print("Created booking for john_doe in Ateneo Room 101.")
    else:
        print("Booking for john_doe in Ateneo Room 101 already exists.")
except Exception as e:
    print("Error creating dummy booking:", e)
