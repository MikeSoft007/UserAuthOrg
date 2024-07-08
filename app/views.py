from flask import Blueprint, request, jsonify, current_app
from .models import db, User, Organization, UserOrganization
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import logging, re
import json
from collections import OrderedDict

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
org_bp = Blueprint('org', __name__, url_prefix='/api/organisations')
user_bp = Blueprint('user', __name__, url_prefix='/api/users')
user_home_bp = Blueprint('home', __name__, url_prefix='')


#Check Connection
@user_home_bp.route('/', methods=['GET'])
def home():
    return jsonify(OrderedDict([
        ("message", "Hi there!, HNG Stage 2 API task connection successful")
    ]))


# Register route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify(OrderedDict([
            ("status", "Bad request"),
            ("message", "Registration unsuccessful"),
            ("statusCode", 400)
        ])), 400

    required_fields = ["firstName", "lastName", "email", "password"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify(OrderedDict([
            ("errors", [{"field": field, "message": f"{field} is required"} for field in missing_fields])
        ])), 422

    # Validate for empty data or spaces and ensure all fields are strings
    empty_or_invalid_fields = [field for field in required_fields if not isinstance(data[field], str) or not data[field].strip()]
    if empty_or_invalid_fields:
        return jsonify(OrderedDict([
            ("errors", [{"field": field, "message": f"{field} cannot be empty, just spaces, or non-string value"} for field in empty_or_invalid_fields])
        ])), 422

    # Validate firstName and lastName to not contain numeric characters
    if any(char.isdigit() for char in data['firstName']):
        return jsonify(OrderedDict([
            ("errors", [{"field": "firstName", "message": "firstName must not contain numeric characters"}])
        ])), 422
    if any(char.isdigit() for char in data['lastName']):
        return jsonify(OrderedDict([
            ("errors", [{"field": "lastName", "message": "lastName must not contain numeric characters"}])
        ])), 422

    # Validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, data['email']):
        return jsonify(OrderedDict([
            ("status", "fail"),
            ("message", "Invalid email format")
        ])), 400

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

        # Generate access token
        access_token = create_access_token(identity=new_user.id)

        response = OrderedDict([
            ("status", "success"),
            ("message", "Registration successful"),
            ("data", OrderedDict([
                ("accessToken", access_token),
                ("user", OrderedDict([
                    ("userId", new_user.id),
                    ("firstName", new_user.first_name),
                    ("lastName", new_user.last_name),
                    ("email", new_user.email),
                    ("phone", new_user.phone)
                ]))
            ]))
        ])

        return current_app.response_class(
            response=json.dumps(response),
            status=201,
            mimetype='application/json'
        )

    except IntegrityError:
        db.session.rollback()
        return jsonify(OrderedDict([
            ("errors", [{"field": "email", "message": "Email already exists"}])
        ])), 422
    

# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(OrderedDict([
            ("status", "Bad request"),
            ("message", "Authentication failed"),
            ("statusCode", 401)
        ])), 401

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        response = OrderedDict([
            ("status", "success"),
            ("message", "Login successful"),
            ("data", OrderedDict([
                ("accessToken", access_token),
                ("user", OrderedDict([
                    ("userId", user.id),
                    ("firstName", user.first_name),
                    ("lastName", user.last_name),
                    ("email", user.email),
                    ("phone", user.phone)
                ]))
            ]))
        ])
        return current_app.response_class(
            response=json.dumps(response),
            status=200,
            mimetype='application/json'
        )
    else:
        return jsonify(OrderedDict([
            ("status", "Bad request"),
            ("message", "Authentication failed"),
            ("statusCode", 401)
        ])), 401


# Get user info
@user_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(id)
    if user.id != current_user_id:
        return jsonify(OrderedDict([
            ("status", "Bad request"),
            ("message", "Access denied"),
            ("statusCode", 403)
        ])), 403

    response = OrderedDict([
        ("status", "success"),
        ("message", "User fetched successfully"),
        ("data", OrderedDict([
            ("userId", user.id),
            ("firstName", user.first_name),
            ("lastName", user.last_name),
            ("email", user.email),
            ("phone", user.phone)
        ]))
    ])
    return current_app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


# Get user's organizations
@org_bp.route('', methods=['GET'])
@jwt_required()
def get_organizations():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    orgs = user.organizations
    response = OrderedDict([
        ("status", "success"),
        ("message", "Organisations fetched successfully"),
        ("data", OrderedDict([
            ("organisations", [{"orgId": org.id, "name": org.name, "description": org.description} for org in orgs])
        ]))
    ])
    return current_app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


# Get single organization
@org_bp.route('/<orgId>', methods=['GET'])
@jwt_required()
def get_organization(orgId):
    org = Organization.query.get_or_404(orgId)
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    if org not in user.organizations:
        return jsonify(OrderedDict([
            ("status", "Bad request"),
            ("message", "Access denied"),
            ("statusCode", 403)
        ])), 403

    response = OrderedDict([
        ("status", "success"),
        ("message", "Organisation fetched successfully"),
        ("data", OrderedDict([
            ("orgId", org.id),
            ("name", org.name),
            ("description", org.description)
        ]))
    ])
    return current_app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


# Create new organization
@org_bp.route('', methods=['POST'])
@jwt_required()
def create_organization():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify(OrderedDict([
            ("status", "Bad Request"),
            ("message", "Name is required")
        ])), 400

    try:
        org = Organization(
            name=name,
            description=description
        )
        db.session.add(org)
        db.session.commit()
        response = OrderedDict([
            ("status", "success"),
            ("message", "Organisation created successfully"),
            ("data", OrderedDict([
                ("orgId", org.id),
                ("name", org.name),
                ("description", org.description)
            ]))
        ])
        return current_app.response_class(
            response=json.dumps(response),
            status=201,
            mimetype='application/json'
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating organization: {str(e)}")
        return jsonify(OrderedDict([
            ("status", "error"),
            ("message", "An error occurred while creating the organization")
        ])), 500
    

# Add user to organization
@org_bp.route('/<orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organization(orgId):
    data = request.get_json()
    if not data or 'userId' not in data:
        return jsonify(OrderedDict([
            ("errors", [{"field": "userId", "message": "userId is required"}])
        ])), 422

    try:
        org = Organization.query.get(orgId)
        if not org:
            return jsonify(OrderedDict([
                ("status", "Bad request"),
                ("message", "Invalid organization ID"),
                ("statusCode", 404)
            ])), 404

        user = User.query.get(data['userId'])
        if not user:
            return jsonify(OrderedDict([
                ("status", "Bad request"),
                ("message", "Invalid user ID"),
                ("statusCode", 404)
            ])), 404

        if user in org.users:
            return jsonify(OrderedDict([
                ("status", "Bad request"),
                ("message", "User already in organization"),
                ("statusCode", 400)
            ])), 400

        user_org = UserOrganization(user_id=user.id, organization_id=org.id)
        db.session.add(user_org)
        db.session.commit()

        response = OrderedDict([
            ("status", "success"),
            ("message", "User added to organization successfully")
        ])
        return current_app.response_class(
            response=json.dumps(response),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding user to organization: {str(e)}")
        return jsonify(OrderedDict([
            ("status", "error"),
            ("message", "An error occurred while adding the user to the organization")
        ])), 500