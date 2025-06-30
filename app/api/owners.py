from flask import request, Blueprint
from flask_restful import Api, Resource
from ..models import Owner
from ..extensions import db
from ..schemas import owner_schema, owners_schema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from ..auth.decorators import admin_required

owners_bp = Blueprint('owners_bp', __name__)
api = Api(owners_bp)

class OwnerListResource(Resource):
    @jwt_required()
    def get(self):
        owners = Owner.query.all()
        return owners_schema.dump(owners)

    @admin_required
    def post(self):
        json_data = request.get_json()
        try:
            new_owner = owner_schema.load(json_data, session=db.session)
            db.session.add(new_owner)
            db.session.commit()
            return owner_schema.dump(new_owner), 201
        except ValidationError as err:
            return err.messages, 422

class OwnerResource(Resource):
    @jwt_required()
    def get(self, owner_id):
        owner = Owner.query.get_or_404(owner_id)
        return owner_schema.dump(owner)

    @admin_required
    def put(self, owner_id):
        owner = Owner.query.get_or_404(owner_id)
        json_data = request.get_json()
        try:
            updated_owner = owner_schema.load(json_data, instance=owner, partial=True, session=db.session)
            db.session.commit()
            return owner_schema.dump(updated_owner)
        except ValidationError as err:
            return err.messages, 422

    @admin_required
    def delete(self, owner_id):
        owner = Owner.query.get_or_404(owner_id)
        db.session.delete(owner)
        db.session.commit()
        return '', 204

api.add_resource(OwnerListResource, '/owners')
api.add_resource(OwnerResource, '/owners/<int:owner_id>')