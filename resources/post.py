from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.post import Post
from models.comment import Comment
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.post_images import PostImage

from extensions import db
from models.post import Post


class PostResource(Resource):

    @jwt_required()
    def post(self):

        data = request.get_json()

        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return {
                "message": "Title and content are required"
            }, 400

        user_id = get_jwt_identity()

        new_post = Post(
            title=title,
            content=content,
            user_id=int(user_id)
        )

        db.session.add(new_post)
        db.session.commit()

        return {
            "message": "Post created successfully",
            "post": {
                "id": new_post.id,
                "title": new_post.title,
                "content": new_post.content,
                "user_id": new_post.user_id
            }
        }, 201

    @jwt_required()
    def put(self):

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

        user_id = get_jwt_identity()

        if post.user_id != int(user_id):
            return {
                "message": "You are not authorized to update this post"
            }, 403

        data = request.get_json()

        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return {
                "message": "Title and content are required"
            }, 400

        post.title = title
        post.content = content

        db.session.commit()

        return {
            "message": "Post updated successfully",
            "post": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "user_id": post.user_id
            }
        }, 200

    @jwt_required()
    def delete(self):

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

        user_id = get_jwt_identity()

        if post.user_id != int(user_id):
            return {
                "message": "You are not authorized to delete this post"
            }, 403

        # Delete comments belonging to this post first
        comments = Comment.query.filter_by(
            post_id=post_id
        ).all()

        for comment in comments:
            db.session.delete(comment)

        # Now delete the post
        db.session.delete(post)

        db.session.commit()

        return {
            "message": "Post deleted successfully"
        }, 200


class PostListResource(Resource):

    def get(self):

        posts = Post.query.all()

        return {
            "posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,

                    "author": {
                        "id": post.author.id,
                        "name": post.author.name
                    },

                    "images": [
                        {
                            "id": image.id,
                            "image_path": image.image_path
                        }
                        for image in post.images
                    ]
                }
                for post in posts
            ]
        }, 200


class SinglePostResource(Resource):

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

        return {
            "post": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "author": {
                    "id": post.author.id,
                    "name": post.author.name
                }
            }
        }, 200