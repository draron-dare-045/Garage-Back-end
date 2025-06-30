from flask import Blueprint
from flask_restful import Api, Resource
from sqlalchemy import func
from ..models import Owner, Garage, ServiceAppointment, Car, ServiceStatusEnum
from ..extensions import db
from ..schemas import CustomerDistributionSchema, GarageWorkloadSchema
from flask_jwt_extended import jwt_required
from ..auth.decorators import manager_required

analytics_bp = Blueprint('analytics_bp', __name__)
api = Api(analytics_bp)

class CustomerDistributionResource(Resource):
    """
    Provides a report on how many unique car owners are associated
    with each garage through service appointments.
    """
    @manager_required
    def get(self):
        # This query joins Garage, ServiceAppointment, Car, and Owner
        # to count distinct owners for each garage.
        query = db.session.query(
            Garage.name,
            func.count(func.distinct(Car.owner_id)).label('owner_count')
        ).join(ServiceAppointment, Garage.id == ServiceAppointment.garage_id)\
         .join(Car, ServiceAppointment.car_id == Car.id)\
         .group_by(Garage.name).all()

        # The schema is not directly used here as the query result is a list of tuples
        # We manually format the response
        result = [{"garage_name": name, "owner_count": count} for name, count in query]
        
        return result, 200

class GarageWorkloadResource(Resource):
    """
    Provides a report on the number of completed vs. scheduled
    appointments for each garage.
    """
    @manager_required
    def get(self):
        # Subquery to count completed appointments for each garage
        completed_sq = db.session.query(
            ServiceAppointment.garage_id,
            func.count(ServiceAppointment.id).label('completed_count')
        ).filter(ServiceAppointment.status == ServiceStatusEnum.completed).group_by(ServiceAppointment.garage_id).subquery()

        # Subquery to count scheduled appointments for each garage
        scheduled_sq = db.session.query(
            ServiceAppointment.garage_id,
            func.count(ServiceAppointment.id).label('scheduled_count')
        ).filter(ServiceAppointment.status == ServiceStatusEnum.scheduled).group_by(ServiceAppointment.garage_id).subquery()

        # Main query to join garage info with the counts
        query = db.session.query(
            Garage.name,
            func.coalesce(completed_sq.c.completed_count, 0),
            func.coalesce(scheduled_sq.c.scheduled_count, 0)
        ).outerjoin(completed_sq, Garage.id == completed_sq.c.garage_id)\
         .outerjoin(scheduled_sq, Garage.id == scheduled_sq.c.garage_id).all()
        
        result = [
            {"garage_name": name, "completed_appointments": comp_count, "scheduled_appointments": sched_count}
            for name, comp_count, sched_count in query
        ]

        return result, 200


api.add_resource(CustomerDistributionResource, '/analytics/customer-distribution')
api.add_resource(GarageWorkloadResource, '/analytics/garage-workload')
