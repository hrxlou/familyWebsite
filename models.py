from extensions import db
from datetime import datetime

class BaseModel(db.Model):
    __abstract__ = True
    
    def to_dict(self):
        """기본적인 딕셔너리 변환 메서드 (상속받아 필요한 경우 오버라이드)"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result


class User(BaseModel):
    __tablename__ = 'users'

    username = db.Column(db.String(50), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    introduction = db.Column(db.String(255))
    avatar_url = db.Column(db.String(255))

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    photos = db.relationship('Photo', backref='uploader', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)


class Post(BaseModel):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    author_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    author_nickname = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, current_username=None):
        like_count = len(self.likes) if self.likes else 0
        liked_by_me = False
        if current_username and self.likes:
            liked_by_me = any(l.username == current_username for l in self.likes)
        return {
            "id": self.id,
            "author_username": self.author_username,
            "author_nickname": self.author_nickname,
            "title": self.title,
            "content": self.content,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "like_count": like_count,
            "liked_by_me": liked_by_me,
            "comments": [comment.to_dict() for comment in self.comments]
        }


class Comment(BaseModel):
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
            "post_id": self.post_id,
            "author_username": self.author_username,
            "author_nickname": self.author_nickname,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Photo(BaseModel):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    uploader_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    uploader_nickname = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(BaseModel):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default='event')
    category = db.Column(db.String(50), default='others')  # 'event', 'holiday', 'anniversary', 'others'
    repeat_type = db.Column(db.String(50), default='none')  # 'none', 'yearly'
    is_lunar = db.Column(db.Boolean, default=False)


class Anniversary(BaseModel):
    __tablename__ = 'anniversaries'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default='anniversary')


class Like(BaseModel):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('post_id', 'username', name='unique_like'),)


class Notification(BaseModel):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Vote(BaseModel):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    author_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    author_nickname = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    options = db.relationship('VoteOption', backref='vote', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, current_username=None):
        total_responses = sum(len(opt.responses) for opt in self.options)
        my_vote = None
        if current_username:
            for opt in self.options:
                for resp in opt.responses:
                    if resp.username == current_username:
                        my_vote = opt.id
                        break
        return {
            "id": self.id,
            "author_username": self.author_username,
            "author_nickname": self.author_nickname,
            "title": self.title,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_responses": total_responses,
            "my_vote": my_vote,
            "options": [opt.to_dict() for opt in self.options]
        }


class VoteOption(BaseModel):
    __tablename__ = 'vote_options'

    id = db.Column(db.Integer, primary_key=True)
    vote_id = db.Column(db.Integer, db.ForeignKey('votes.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)

    responses = db.relationship('VoteResponse', backref='option', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "count": len(self.responses),
        }


class VoteResponse(BaseModel):
    __tablename__ = 'vote_responses'

    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey('vote_options.id'), nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('option_id', 'username', name='unique_vote_response'),)
