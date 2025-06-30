from flask import request, Blueprint
from flask_restful import Api, Resource
from ..models import Car, Garage
from ..extensions import db
from ..schemas import car_schema, cars_schema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from ..auth.decorators import manager_required, admin_required

cars_bp = Blueprint('cars_bp', __name__)
api = Api(cars_bp)

class CarListResource(Resource):
    @jwt_required()
    def get(self):
        cars = Car.query.all()
        return cars_schema.dump(cars)

    @jwt_required()
    def post(self):
        json_data = request.get_json()
        try:
            new_car = car_schema.load(json_data, session=db.session)
            db.session.add(new_car)
            db.session.commit()
            return car_schema.dump(new_car), 201
        except ValidationError as err:
            return err.messages, 422
        except Exception as e:
            db.session.rollback()
            return {"message": f"An unexpected error occurred: {str(e)}"}, 500

class CarResource(Resource):
    @jwt_required()
    def get(self, car_id):
        car = Car.query.get_or_404(car_id)
        return car_schema.dump(car)

    @jwt_required()
    def put(self, car_id):
        car = Car.query.get_or_404(car_id)
        json_data = request.get_json()
        try:
            updated_car = car_schema.load(json_data, instance=car, partial=True, session=db.session)
            db.session.commit()
            return car_schema.dump(updated_car)
        except ValidationError as err:
            return err.messages, 422

    @admin_required
    def delete(self, car_id):
        car = Car.query.get_or_404(car_id)
        db.session.delete(car)
        db.session.commit()
        return '', 204

class CarGarageLinkResource(Resource):
    @manager_required
    def post(self, car_id, garage_id):
        """Link a car to a garage as a preferred garage."""
        car = Car.query.get_or_404(car_id)
        garage = Garage.query.get_or_404(garage_id)

        if garage in car.preferred_garages:
            return {'message': 'Car is already linked to this garage'}, 409
        
        car.preferred_garages.append(garage)
        db.session.commit()
        return {'message': f'Car {car_id} successfully linked to Garage {garage_id}'}, 200

    @manager_required
    def delete(self, car_id, garage_id):
        """Unlink a car from a garage."""
        car = Car.query.get_or_404(car_id)
        garage = Garage.query.get_or_404(garage_id)

        if garage not in car.preferred_garages:
            return {'message': 'This car is not linked to the specified garage'}, 404
            
        car.preferred_garages.remove(garage)
        db.session.commit()
        return {'message': f'Car {car_id} successfully unlinked from Garage {garage_id}'}, 200


api.add_resource(CarListResource, '/cars')
api.add_resource(CarResource, '/cars/<int:car_id>')
api.add_resource(CarGarageLinkResource, '/cars/<int:car_id>/garages/<int:garage_id>')
