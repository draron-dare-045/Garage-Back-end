from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum as SQLAlchemyEnum
# Correctly import 'db' from the new central extensions module
from .extensions import db
import enum

# Association table for the many-to-many relationship between Cars and Garages
garage_car_association = db.Table('garage_car',
    db.Column('car_id', db.Integer, db.ForeignKey('car.id'), primary_key=True),
    db.Column('garage_id', db.Integer, db.ForeignKey('garage.id'), primary_key=True)
)

class RoleEnum(enum.Enum):
    owner = 'owner'
    manager = 'manager'
    admin = 'admin'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(SQLAlchemyEnum(RoleEnum), nullable=False, default=RoleEnum.owner)

    # Optional links to other models if a user directly corresponds to an owner or garage manager
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=True)
    garage_id = db.Column(db.Integer, db.ForeignKey('garage.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    cars = db.relationship('Car', backref='owner', lazy=True, cascade="all, delete-orphan")
    user = db.relationship('User', backref='owner_profile', uselist=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    appointments = db.relationship('ServiceAppointment', backref='car', lazy=True, cascade="all, delete-orphan")
    
    # Many-to-many relationship with Garage
    preferred_garages = db.relationship('Garage', secondary=garage_car_association, back_populates='preferred_cars')


class Garage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, default=10)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    appointments = db.relationship('ServiceAppointment', backref='garage', lazy=True, cascade="all, delete-orphan")
    user = db.relationship('User', backref='garage_profile', uselist=False)
    
    # Many-to-many relationship with Car
    preferred_cars = db.relationship('Car', secondary=garage_car_association, back_populates='preferred_garages')

class ServiceStatusEnum(enum.Enum):
    scheduled = 'scheduled'
    completed = 'completed'
    canceled = 'canceled'

class ServiceAppointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    garage_id = db.Column(db.Integer, db.ForeignKey('garage.id'), nullable=False)
    service_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(SQLAlchemyEnum(ServiceStatusEnum), nullable=False, default=ServiceStatusEnum.scheduled)
