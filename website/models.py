from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    photo = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    rounds_played = db.relationship(
        'Rounds', secondary='user_rounds', back_populates='players')
    games_created = db.relationship('Games', back_populates='created_by_user')


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    position = db.Column(db.Integer)
    price = db.Column(db.String(150))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    rounds_played = db.relationship(
        'Rounds', back_populates='game', cascade="all,delete")
    created_by_user = db.relationship('User', back_populates='games_created')


class Rounds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    victory = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    game_number = db.Column(db.Integer, db.ForeignKey('games.id'))
    players = db.relationship(
        'User', secondary='user_rounds', back_populates='rounds_played')
    game = db.relationship('Games', back_populates='rounds_played')


user_rounds = db.Table('user_rounds',
                       db.Column('user_id', db.Integer,
                                 db.ForeignKey('user.id')),
                       db.Column('round_id', db.Integer,
                                 db.ForeignKey('rounds.id'))
                       )
