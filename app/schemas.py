from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, validate
from .models import Owner, Car, Garage, ServiceAppointment, User, RoleEnum, ServiceStatusEnum

class UserSchema(SQLAlchemyAutoSchema):
    # Use load_only for the password field so it's not exposed in API responses
    password = fields.Str(required=True, load_only=True)
    role = fields.Enum(RoleEnum, by_value=True)

    class Meta:
        model = User
        load_instance = True
        include_fk = True
        # Exclude the password hash from serialization
        exclude = ('password_hash',)

class OwnerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Owner
        load_instance = True
        include_relationships = True

class CarSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Car
        load_instance = True
        include_relationships = True
        include_fk = True # To show owner_id

class GarageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Garage
        load_instance = True
        include_relationships = True

class ServiceAppointmentSchema(SQLAlchemyAutoSchema):
    status = fields.Enum(ServiceStatusEnum, by_value=True)

    class Meta:
        model = ServiceAppointment
        load_instance = True
        include_relationships = True
        include_fk = True

# Schemas for analytics
class CustomerDistributionSchema(fields.Dict):
    garage_name = fields.Str()
    owner_count = fields.Int()

class GarageWorkloadSchema(fields.Dict):
    garage_name = fields.Str()
    completed_appointments = fields.Int()
    scheduled_appointments = fields.Int()

# Instantiate schemas for use in resources
user_schema = UserSchema()
owner_schema = OwnerSchema()
owners_schema = OwnerSchema(many=True)
car_schema = CarSchema()
cars_schema = CarSchema(many=True)
garage_schema = GarageSchema()
garages_schema = GarageSchema(many=True)
service_appointment_schema = ServiceAppointmentSchema()
service_appointments_schema = ServiceAppointmentSchema(many=True)
