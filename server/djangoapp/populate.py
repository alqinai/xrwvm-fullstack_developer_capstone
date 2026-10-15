from django.db import transaction
from .models import CarMake, CarModel


@transaction.atomic
def initiate():
    car_make_data = [
        ("NISSAN", "Great cars. Japanese technology", [("Pathfinder", "SUV"), ("Qashqai", "SUV"), ("XTRAIL", "SUV")]),
        ("Mercedes", "Great cars. German technology", [("A-Class", "SUV"), ("C-Class", "SUV"), ("E-Class", "SUV")]),
        ("Audi", "Great cars. German technology", [("A4", "SUV"), ("A5", "SUV"), ("A6", "SUV")]),
        ("Kia", "Great cars. Korean technology", [("Sorrento", "SUV"), ("Carnival", "SUV"), ("Cerato", "Sedan")]),
        ("Toyota", "Great cars. Japanese technology", [("Corolla", "Sedan"), ("Camry", "Sedan"), ("Kluger", "SUV")]),
    ]
    for make_name, description, cars in car_make_data:
        make, _ = CarMake.objects.get_or_create(
            name=make_name, defaults={"description": description}
        )
        for name, car_type in cars:
            CarModel.objects.get_or_create(
                car_make=make, name=name,
                defaults={"type": car_type, "year": 2023, "dealer_id": 0}
            )
