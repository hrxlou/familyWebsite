from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    username = db.Column(db.String(50), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    introduction = db.Column(db.String(255))
    avatar_url = db.Column(db.String(255))
    
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    photos = db.relationship('Photo', backref='uploader', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    author_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    author_nickname = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            "id": self.id,
            "author_username": self.author_username,
            "author_nickname": self.author_nickname,
            "title": self.title,
            "content": self.content,
            "image_url": self.image_url,
            "comments": [comment.to_dict() for comment in self.comments]
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    author_nickname = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "author_username": self.author_username,
            "author_nickname": self.author_nickname,
            "content": self.content
        }

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    uploader_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    uploader_nickname = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "url": self.url,
            "uploader_username": self.uploader_username,
            "uploader_nickname": self.uploader_nickname
        }

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default='event')
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "type": self.type
        }

class Anniversary(db.Model):
    __tablename__ = 'anniversaries'
    
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default='anniversary')
    
    def to_dict(self):
        return {
            "id": self.id,
            "month": self.month,
            "day": self.day,
            "title": self.title,
            "type": self.type
        }
