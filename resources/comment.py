from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.comment import Comment
from models.post import Post


class CommentResource(Resource):
    @jwt_required()
    def post(self):

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

        data = request.get_json()

        content = data.get("content")

        if not content:
            return {
                "message": "Comment content is required"
            }, 400

        user_id = get_jwt_identity()

        new_comment = Comment(
            content=content,
            user_id=int(user_id),
            post_id=post_id
        )

        db.session.add(new_comment)
        db.session.commit()

        return {
            "message": "Comment added successfully",
            "comment": {
                "id": new_comment.id,
                "content": new_comment.content,
                "user_id": new_comment.user_id,
                "post_id": new_comment.post_id,
                "created_at": new_comment.created_at.isoformat()
            }
        }, 
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

        comments = Comment.query.filter_by(post_id=post_id).all()

        return {
            "comments": [
                {
                    "id": comment.id,
                    "content": comment.content,
                     "author": {
                            "id": comment.comment_author.id,
                            "name": comment.comment_author.name
                            },
                    "post_id": comment.post_id,
                    "created_at": comment.created_at.isoformat()
                }
                for comment in comments
            ]
        }, 200
    @jwt_required()
    def delete(self):

        comment_id = request.args.get("comment_id", type=int)

        if not comment_id:
            return {
                "message": "comment_id is required"
            }, 400

        comment = Comment.query.get(comment_id)

        if not comment:
            return {
                "message": "Comment not found"
            }, 404

        user_id = get_jwt_identity()

        if comment.user_id != int(user_id):
            return {
                "message": "You are not authorized to delete this comment"
            }, 403

        db.session.delete(comment)
        db.session.commit()

        return {
            "message": "Comment deleted successfully"
        }, 200