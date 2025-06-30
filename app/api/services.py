from flask import request, Blueprint, jsonify
from flask_restful import Api, Resource
from ..models import ServiceAppointment, Garage, ServiceStatusEnum
from ..extensions import db
from ..schemas import service_appointment_schema, service_appointments_schema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt
from ..auth.decorators import manager_required

services_bp = Blueprint('services_bp', __name__)
api = Api(services_bp)

class ServiceAppointmentListResource(Resource):
    @jwt_required()
    def get(self):
        # Allow filtering by car_id or garage_id
        car_id = request.args.get('car_id', type=int)
        garage_id = request.args.get('garage_id', type=int)
        
        query = ServiceAppointment.query
        
        if car_id:
            query = query.filter_by(car_id=car_id)
        if garage_id:
            query = query.filter_by(garage_id=garage_id)
            
        appointments = query.all()
        return service_appointments_schema.dump(appointments)

    @jwt_required()
    def post(self):
        json_data = request.get_json()
        garage_id = json_data.get('garage_id')
        
        if not garage_id:
            return {'message': 'garage_id is required'}, 400
            
        garage = Garage.query.get_or_404(garage_id)
        
        # Check garage capacity
        active_appointments = ServiceAppointment.query.filter_by(
            garage_id=garage_id,
            status=ServiceStatusEnum.scheduled
        ).count()
        
        if active_appointments >= garage.capacity:
            return {'message': f'Garage is at full capacity ({garage.capacity} appointments). Cannot schedule new service.'}, 409

        try:
            new_appointment = service_appointment_schema.load(json_data, session=db.session)
            db.session.add(new_appointment)
            db.session.commit()
            return service_appointment_schema.dump(new_appointment), 201
        except ValidationError as err:
            return err.messages, 422

class ServiceAppointmentResource(Resource):
    @jwt_required()
    def get(self, appointment_id):
        appointment = ServiceAppointment.query.get_or_404(appointment_id)
        return service_appointment_schema.dump(appointment)

    @manager_required
    def put(self, appointment_id):
        appointment = ServiceAppointment.query.get_or_404(appointment_id)
        json_data = request.get_json()
        
        # Security check: Ensure manager can only edit appointments for their garage
        claims = get_jwt()
        garage_id_from_token = claims.get('garage_id')
        if claims.get('roles') == 'manager' and appointment.garage_id != garage_id_from_token:
            return {'message': 'Forbidden: You can only modify appointments for your own garage.'}, 403

        try:
            updated_appointment = service_appointment_schema.load(json_data, instance=appointment, partial=True, session=db.session)
            db.session.commit()
            return service_appointment_schema.dump(updated_appointment)
        except ValidationError as err:
            return err.messages, 422

    @manager_required
    def delete(self, appointment_id):
        appointment = ServiceAppointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return '', 204

api.add_resource(ServiceAppointmentListResource, '/services')
api.add_resource(ServiceAppointmentResource, '/services/<int:appointment_id>')
