import flask
from flask import Blueprint, request, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime
import jwt

from .models import User, JWTBlacklist
from . import db
SECRET_KEY = 'demo'

auth_blueprint = Blueprint('auth_view', __name__)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    password_hash = generate_password_hash(password).decode('utf-8')

    print(f'{username}\n{email}\n{password}\n{password_hash}')

    try:
        user_exists = db.session.query(User.id).filter_by(email=email).first()
        if user_exists:
            return jsonify({'message': 'User already exists.'}), 409

        new_user = User(
            username = username,
            email = email, 
            password_hash = password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        print(f'New user added: {username}')
        return {'message': 'Success'}, 201

    except Exception as e:
        print(f'Error: {e}')

    return {'message': 'Failed to retrieve data'}, 400

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    password_hash = generate_password_hash(password).decode('utf-8')

    print(f'{email}\n{password}\n{password_hash}')

    try:
        user = db.session.query(User).filter_by(email=email).first()
        print('User is retrieved from the DB.')

        if not user:
            print('User not found.')
            return {'message': 'Invalid login credentials.'}, 404

        print('User is found.')

        if check_password_hash(user.password_hash, password):
            auth_token = generate_jwt(user.id)
            print(auth_token)
            if auth_token:
                return {
                    'auth_token': auth_token
                }, 201
        else:
            print('Hashes do not match.')
            print('Wrong password.')
            return {'message': 'Invalid login credentials.'}, 401

    except Exception as e:
        print(f'Error: {e}')

    return {'message': 'Failed to retrieve data'}, 400

@auth_blueprint.route('/get_user_id')
def fetch_user_id():
    user_id = request.get_json().get('user_id')
    fetched_user = db.session.query(User).filter_by(user_id=user_id).first()
    return {'fetched_user_id': fetched_user.id}, 201

@auth_blueprint.route('/verify_jwt', methods=['POST'])
def verify_jwt():
    access_token = request.get_json().get('JWT')
    user_id = decode_jwt(access_token)
    # if the function returns a string, this means an error has occurred
    if isinstance(user_id, str):
        return {'message': 'Invalid authentication token.'}, 403
    else:
        return {'user_id': user_id}, 201

def generate_jwt(user_id):
    """
    Generates authentication token
    :return: string (JWT)
    """
    try:
        payload = {
            # subject
            'sub':user_id,
            # expire
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=0, minutes=30),
            # issued at
            'iat': datetime.datetime.now(datetime.UTC)
        }
        print(payload)
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return f'Error: {e}'

def decode_jwt(access_token):
    """
    Decode a JWT and return a user ID if the token has not expired
    :param access_token: JWT string
    :return: integer|string
    """
    try:
        payload = jwt.decode(access_token, SECRET_KEY)
        print(payload)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Session has expired. Please, log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid authentication token. Please, log in again.'


@auth_blueprint.route('/invalidate_jwt', methods=['POST'])
def invalidate_jwt():
    # invalidating the JWT by storing it in the JWT blacklist
    access_token = request.get_json().get('access_token')
    print(access_token)
    sub = decode_jwt(access_token)
    try:
        if isinstance(sub, str):
            print(sub)
            return {'message': 'Failed to decode the token.'}, 400
        else:
            blacklist_token = JWTBlacklist(token=access_token)
            db.session.add(blacklist_token)
            db.session.commit()
            return {'message': 'The JWt is successfully invalidated.'}, 201
    except Exception as e:
        message = f'Error during JWT invalidation: {e}'
        print(message)
        return f'Error: {e}'

