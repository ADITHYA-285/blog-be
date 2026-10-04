from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token

from extensions import db
from models.user import User
from utils.auth import hash_password, check_password


class RegisterResource(Resource):

    def post(self):
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return {
                "message": "Name, email and password are required"
            }, 400

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return {
                "message": "Email already registered"
            }, 409

        hashed_password = hash_password(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email
            }
        }, 201

    
class LoginResource(Resource):

    def post(self):
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {
                "message": "Email and password are required"
            }, 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return {
                "message": "Invalid email or password"
            }, 401

        if not check_password(password, user.password):
            return {
                "message": "Invalid email or password"
            }, 401

        access_token = create_access_token(
            identity=str(user.id)
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }, 200