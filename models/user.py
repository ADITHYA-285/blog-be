from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow )
    posts = db.relationship("Post", backref="author", lazy=True)
    comments = db.relationship("Comment",backref="comment_author",lazy=True)