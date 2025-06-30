from flask import request, Blueprint
from flask_restful import Api, Resource
from ..models import Garage
from ..extensions import db
from ..schemas import garage_schema, garages_schema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from ..auth.decorators import admin_required, manager_required

garages_bp = Blueprint('garages_bp', __name__)
api = Api(garages_bp)

class GarageListResource(Resource):
    def get(self):
        """Garages are public information"""
        garages = Garage.query.all()
        return garages_schema.dump(garages)

    @admin_required
    def post(self):
        json_data = request.get_json()
        try:
            new_garage = garage_schema.load(json_data, session=db.session)
            db.session.add(new_garage)
            db.session.commit()
            return garage_schema.dump(new_garage), 201
        except ValidationError as err:
            return err.messages, 422

class GarageResource(Resource):
    def get(self, garage_id):
        """Garage details are public"""
        garage = Garage.query.get_or_404(garage_id)
        return garage_schema.dump(garage)

    @manager_required
    def put(self, garage_id):
        garage = Garage.query.get_or_404(garage_id)
        json_data = request.get_json()
        try:
            updated_garage = garage_schema.load(json_data, instance=garage, partial=True, session=db.session)
            db.session.commit()
            return garage_schema.dump(updated_garage)
        except ValidationError as err:
            return err.messages, 422

    @admin_required
    def delete(self, garage_id):
        garage = Garage.query.get_or_404(garage_id)
        db.session.delete(garage)
        db.session.commit()
        return '', 204

api.add_resource(GarageListResource, '/garages')
api.add_resource(GarageResource, '/garages/<int:garage_id>')
