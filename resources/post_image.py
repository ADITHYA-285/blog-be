import os
import uuid

from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from extensions import db
from models.post import Post
from models.post_images import PostImage


class PostImageResource(Resource):

    @jwt_required()
    def post(self):

        # Get post ID
        post_id = request.args.get("post_id", type=int)

        if not post_id:
            return {
                "message": "post_id is required"
            }, 400

        # Check whether post exists
        post = Post.query.get(post_id)

        if not post:
            return {
                "message": "Post not found"
            }, 404

        # Check whether image was sent
        if "image" not in request.files:
            return {
                "message": "Image is required"
            }, 400

        image = request.files["image"]

        # Check filename
        if image.filename == "":
            return {
                "message": "No image selected"
            }, 400

        # Create safe filename
        filename = secure_filename(image.filename)

        # Add unique value to filename
        unique_filename = (
            str(uuid.uuid4()) + "_" + filename
        )

        # Create upload path
        upload_folder = current_app.config["UPLOAD_FOLDER"]

        file_path = os.path.join(
            upload_folder,
            unique_filename
        )

        # Save image
        image.save(file_path)

        # Save image information in database
        new_image = PostImage(
            image_path=unique_filename,
            post_id=post_id
        )

        db.session.add(new_image)
        db.session.commit()

        return {
            "message": "Image uploaded successfully",
            "image": {
                "id": new_image.id,
                "image_path": new_image.image_path,
                "post_id": new_image.post_id
            }
        }, 201
    def get(self):

        post_id = request.args.get("post_id", type=int)

        if not post_id:
            return {
                "message": "post_id is required"
            }, 400

        post = Post.query.get(post_id)

        if not post:
            return {
                "message": "Post not found"
            }, 404

        images = PostImage.query.filter_by(
            post_id=post_id
        ).all()

        return {
            "images": [
                {
                    "id": image.id,
                    "image_path": image.image_path,
                    "post_id": image.post_id,
                    "created_at": image.created_at.isoformat()
                }
                for image in images
            ]
        }, 200
    @jwt_required()
    def delete(self):

        image_id = request.args.get("image_id", type=int)

        if not image_id:
            return {
                "message": "image_id is required"
            }, 400

        image = PostImage.query.get(image_id)

        if not image:
            return {
                "message": "Image not found"
            }, 404

        post = Post.query.get(image.post_id)

        user_id = get_jwt_identity()

        if post.user_id != int(user_id):
            return {
                "message": "You are not authorized to delete this image"
            }, 403

        upload_folder = current_app.config["UPLOAD_FOLDER"]

        file_path = os.path.join(
            upload_folder,
            image.image_path
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(image)
        db.session.commit()

        return {
            "message": "Image deleted successfully"
        }, 200