from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import uuid
from .utils.generator_short_id import generate_short_id

# Tabla intermedia para los jugadores en cada ronda
user_rounds = db.Table(
    'user_rounds',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('round_id', db.Integer, db.ForeignKey('rounds.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    photo = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)

    # Relaciones
    rounds_played = db.relationship('Rounds', secondary='user_rounds', back_populates='players')
    games_created = db.relationship('Games', back_populates='created_by_user')
    convocations_invited = db.relationship('ConvocationUser', back_populates='user', cascade='all, delete')
    devices = db.relationship('UserDevice', back_populates='user', cascade='all, delete')

class UserDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    onesignal_id = db.Column(db.String(200), nullable=False)  # player_id de OneSignal
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

    # Relación
    user = db.relationship('User', back_populates='devices')

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    position = db.Column(db.Integer)
    price = db.Column(db.String(150))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relaciones
    rounds_played = db.relationship('Rounds', back_populates='game', cascade="all, delete")
    created_by_user = db.relationship('User', back_populates='games_created')

class Rounds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    victory = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    game_number = db.Column(db.Integer, db.ForeignKey('games.id'))

    # Relaciones
    players = db.relationship('User', secondary='user_rounds', back_populates='rounds_played')
    game = db.relationship('Games', back_populates='rounds_played')

class Convocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)  # Fecha del evento
    place = db.Column(db.String(150), nullable=False)  # Lugar del evento
    token = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))  # Enlace único
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Admin que creó el evento
    short_id = db.Column(db.String(4), unique=True, nullable=False, default=lambda: generate_short_id(Convocation))

    # Relaciones
    invited_users = db.relationship('ConvocationUser', back_populates='convocation', cascade='all, delete')
    creator = db.relationship('User')

class ConvocationUser(db.Model):
    convocation_id = db.Column(db.Integer, db.ForeignKey('convocation.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    notification_sent = db.Column(db.Boolean, default=False)  # Rastrear si se envió el recordatorio

    # Relaciones
    convocation = db.relationship('Convocation', back_populates='invited_users')
    user = db.relationship('User', back_populates='convocations_invited')