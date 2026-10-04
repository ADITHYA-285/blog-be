from extensions import db
from datetime import datetime


class PostImage(db.Model):

    __tablename__ = "post_images"

    id = db.Column(db.Integer,primary_key=True)
    image_path = db.Column(db.String(255),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    post_id = db.Column(db.Integer,db.ForeignKey("posts.id"),nullable=False)
    post = db.relationship("Post",backref=db.backref("images",lazy=True,cascade="all, delete-orphan"))