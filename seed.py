"""
Seed file to populate the database with initial data for testing and demonstration.
To run this script: `python seed.py`
"""

from app import create_app, db
from app.models import Owner, Car, Garage, ServiceAppointment, User, RoleEnum, ServiceStatusEnum
from datetime import datetime, timedelta

def seed_data():
    # Create an application context
    app = create_app('development')
    with app.app_context():
        print("--- Starting database seed ---")
        
        # Clean up existing data to avoid duplicates
        # This is important if you run the seed script more than once
        print("... Deleting existing data")
        db.session.query(ServiceAppointment).delete()
        db.session.query(User).delete()
        db.session.query(Car).delete()
        db.session.query(Garage).delete()
        db.session.query(Owner).delete()
        db.session.commit()

        # --- Create Owners ---
        print("... Creating owners")
        owner1 = Owner(name="Alice Wonder", email="alice@example.com", phone="111-222-3333", address="123 Wonderland")
        owner2 = Owner(name="Bob Builder", email="bob@example.com", phone="444-555-6666", address="456 Build St")
        owner3 = Owner(name="Charlie Chocolate", email="charlie@example.com", phone="777-888-9999", address="789 Factory Ln")
        db.session.add_all([owner1, owner2, owner3])
        db.session.commit()

        # --- Create Garages ---
        print("... Creating garages")
        garage1 = Garage(name="Dave's Auto Repair", location="101 Mechanic Ave", capacity=15, phone="123-456-7890", email="contact@davesauto.com")
        garage2 = Garage(name="Sara's Super Service", location="202 Gearhead Rd", capacity=25, phone="098-765-4321", email="support@saraservice.com")
        db.session.add_all([garage1, garage2])
        db.session.commit()

        # --- Create Users and link them ---
        print("... Creating users")
        admin_user = User(username='admin_user', role=RoleEnum.admin)
        admin_user.set_password('adminpass123')
        
        # Link manager to their garage
        manager_user_1 = User(username='manager_dave', role=RoleEnum.manager, garage_id=garage1.id)
        manager_user_1.set_password('managerpass123')
        
        # Link owner to their profile
        owner_user_1 = User(username='alice_owner', role=RoleEnum.owner, owner_id=owner1.id)
        owner_user_1.set_password('ownerpass123')

        db.session.add_all([admin_user, manager_user_1, owner_user_1])
        db.session.commit()
        
        # --- Create Cars ---
        print("... Creating cars")
        car1 = Car(make="Toyota", model="Camry", year=2021, vin="VIN12345ALICE", owner_id=owner1.id)
        car2 = Car(make="Honda", model="Civic", year=2020, vin="VIN67890ALICE", owner_id=owner1.id)
        car3 = Car(make="Ford", model="F-150", year=2022, vin="VINABCDEFBOB", owner_id=owner2.id)
        car4 = Car(make="Tesla", model="Model 3", year=2023, vin="VINFEDCBACHARLIE", owner_id=owner3.id)

        # Link preferred garages
        car1.preferred_garages.append(garage1)
        car3.preferred_garages.append(garage1)
        car3.preferred_garages.append(garage2)
        car4.preferred_garages.append(garage2)
        db.session.add_all([car1, car2, car3, car4])
        db.session.commit()

        # --- Create Service Appointments ---
        print("... Creating service appointments")
        today = datetime.utcnow()
        appt1 = ServiceAppointment(car_id=car1.id, garage_id=garage1.id, service_date=today + timedelta(days=5), description="Oil change and tire rotation", status=ServiceStatusEnum.scheduled)
        appt2 = ServiceAppointment(car_id=car3.id, garage_id=garage1.id, service_date=today - timedelta(days=10), description="Brake pad replacement", status=ServiceStatusEnum.completed)
        appt3 = ServiceAppointment(car_id=car4.id, garage_id=garage2.id, service_date=today + timedelta(days=2), description="Battery check", status=ServiceStatusEnum.scheduled)
        
        db.session.add_all([appt1, appt2, appt3])
        
        # --- Final Commit ---
        db.session.commit()
        print("--- Database has been seeded successfully! ---")

if __name__ == '__main__':
    seed_data()
