from django.core.management.base import BaseCommand
from booking.models import Equipment, Room

class Command(BaseCommand):
    help = "Populates the database with dummy data for rooms and equipment."

    def handle(self, *args, **options):
        # Define common equipment items
        equipment_names = [
            "Projector",
            "Sound System",
            "Whiteboard",
            "Microphone",
            "Stage Lighting",
            "WiFi",
            "Video Conferencing Equipment",
            "Conference Phone",
            "TV"
        ]

        equipment_objs = {}
        for name in equipment_names:
            eq, created = Equipment.objects.get_or_create(name=name)
            equipment_objs[name] = eq
            self.stdout.write(f"{'Created' if created else 'Exists'}: {eq.name}")

        # Example rooms with associated equipment
        rooms_data = [
            {
                "name": "Ateneo Main Hall",
                "description": "Spacious hall for major events.",
                "capacity": 500,
                "location": "Main Building",
                "equipment": ["Sound System", "Projector", "Stage Lighting"]
            },
            {
                "name": "Ateneo Room 101",
                "description": "Ideal for small meetings and study sessions.",
                "capacity": 30,
                "location": "Building A, Floor 1",
                "equipment": ["Whiteboard", "TV"]
            },
            {
                "name": "Ateneo Conference Room",
                "description": "Professional setting for conferences and seminars.",
                "capacity": 100,
                "location": "Building B, Floor 2",
                "equipment": ["Projector", "Conference Phone"]
            },
            {
                "name": "Ateneo Rehearsal Space",
                "description": "Acoustic-friendly space for rehearsals.",
                "capacity": 50,
                "location": "Building C, Basement",
                "equipment": ["Sound System", "Microphone"]
            },
            {
                "name": "Ateneo Auditorium",
                "description": "Large auditorium for presentations and performances.",
                "capacity": 300,
                "location": "Main Auditorium",
                "equipment": ["Stage Lighting", "Sound System", "TV"]
            },
        ]

        for rdata in rooms_data:
            room, created = Room.objects.get_or_create(
                name=rdata["name"],
                defaults={
                    "description": rdata["description"],
                    "capacity": rdata["capacity"],
                    "location": rdata["location"],
                }
            )
            if created:
                self.stdout.write(f"Created room: {room.name}")
            else:
                self.stdout.write(f"Room {room.name} already exists.")

            # Set equipment for the room
            for eq_name in rdata["equipment"]:
                eq = equipment_objs.get(eq_name)
                if eq:
                    room.equipment.add(eq)
            room.save()
