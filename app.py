from flask import Flask
from flask_restful import Api
from config import Config
from extensions import db, bcrypt, jwt
from models.user import User
from flask import Flask, request, jsonify
from config import Config
from extensions import db, bcrypt, jwt
from models.user import User
from utils.auth import check_password, hash_password
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from resources.test import TestResource
from resources.auth import RegisterResource, LoginResource
from resources.post import (PostResource,PostListResource,SinglePostResource)
from flask import send_from_directory
from resources.comment import CommentResource
from resources.post_image import PostImageResource
from flask_cors import CORS
import os



def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "uploads"
)

    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    api = Api(app)
    api.add_resource(TestResource, "/api/test")
    api.add_resource(RegisterResource,"/api/auth/register")
    api.add_resource(LoginResource,"/api/auth/login")
    api.add_resource(PostResource, "/api/posts")
    api.add_resource(PostListResource, "/api/posts")
    api.add_resource(SinglePostResource, "/api/post")
    api.add_resource(CommentResource,"/api/comments")
    api.add_resource(PostImageResource,"/api/post-images")
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename
        )

    return app


app = create_app()

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "message": "Email already registered"
        }), 409

    hashed_password = hash_password(password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password(password, user.password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200

@app.route("/api/auth/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    }), 200

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)