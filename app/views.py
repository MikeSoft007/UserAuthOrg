from flask import Blueprint, request, jsonify
from .models import db, User, Organization, UserOrganization
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
org_bp = Blueprint('org', __name__, url_prefix='/api/organisations')
user_bp = Blueprint('user', __name__, url_prefix='/api/users')

# Registration route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"status": "Bad request", "message": "Registration unsuccessful", "statusCode": 400}), 400
    
    required_fields = ["firstName", "lastName", "email", "password"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"errors": [{"field": field, "message": f"{field} is required"} for field in missing_fields]}), 422
    
    try:
        new_user = User(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            password=data['password'],
            phone=data.get('phone')
        )
        db.session.add(new_user)
        db.session.commit()
        
        org_name = f"{new_user.first_name}'s Organisation"
        new_org = Organization(name=org_name)
        db.session.add(new_org)
        db.session.commit()
        
        user_org = UserOrganization(user_id=new_user.id, organization_id=new_org.id)
        db.session.add(user_org)
        db.session.commit()
        
        access_token = create_access_token(identity=new_user.id)
        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": new_user.id,
                    "firstName": new_user.first_name,
                    "lastName": new_user.last_name,
                    "email": new_user.email,
                    "phone": new_user.phone
                }
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": [{"field": "email", "message": "Email already exists"}]}), 422

# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}), 401

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": user.id,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "email": user.email,
                    "phone": user.phone
                }
            }
        }), 200
    else:
        return jsonify({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}), 401

# Get user info
#@user_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(id)
    if user.id != current_user_id:
        return jsonify({"status": "Bad request", "message": "Access denied", "statusCode": 403}), 403

    return jsonify({
        "status": "success",
        "message": "User fetched successfully",
        "data": {
            "userId": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "phone": user.phone
        }
    }), 200

# Get user's organizations
@org_bp.route('', methods=['GET'])
@jwt_required()
def get_organizations():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    orgs = user.organizations
    return jsonify({
        "status": "success",
        "message": "Organisations fetched successfully",
        "data": {
            "organisations": [{"orgId": org.id, "name": org.name, "description": org.description} for org in orgs]
        }
    }), 200

# Get single organization
@org_bp.route('/<orgId>', methods=['GET'])
@jwt_required()
def get_organization(orgId):
    org = Organization.query.get_or_404(orgId)
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    if org not in user.organizations:
        return jsonify({"status": "Bad request", "message": "Access denied", "statusCode": 403}), 403

    return jsonify({
        "status": "success",
        "message": "Organisation fetched successfully",
        "data": {
            "orgId": org.id,
            "name": org.name,
            "description": org.description
        }
    }), 200

# Create new organization
@org_bp.route('', methods=['POST'])
@jwt_required()
def create_organization():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"errors": [{"field": "name", "message": "name is required"}]}), 422

    current_user_id = get_jwt_identity()
    new_org = Organization(name=data['name'], description=data.get('description'))
    db.session.add(new_org)
    db.session.commit()
    
    user_org = UserOrganization(user_id=current_user_id, organization_id=new_org.id)
    db.session.add(user_org)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Organisation created successfully",
        "data": {
            "orgId": new_org.id,
            "name": new_org.name,
            "description": new_org.description
        }
    }), 201

# Add user to organization
@org_bp.route('/<orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organization(orgId):
    data = request.get_json()
    if not data or 'userId' not in data:
        return jsonify({"errors": [{"field": "userId", "message": "userId is required"}]}), 422

    org = Organization.query.get_or_404(orgId)
    user = User.query.get_or_404(data['userId'])

    if user in org.users:
        return jsonify({"status": "Bad request", "message": "User already in organisation", "statusCode": 400}), 400

    user_org = UserOrganization(user_id=user.id, organization_id=org.id)
    db.session.add(user_org)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User added to organisation successfully"
    }), 200
