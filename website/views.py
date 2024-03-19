from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Games, User, Rounds
from .sql import *
import json
import math
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
from sqlalchemy import desc, text
from functools import wraps

views = Blueprint('views', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'is_admin'):
            flash('No eres administrador, no puedes entrar aquí.', category='error')
            # redirigir a la página de inicio de sesión si el usuario no está autenticado o no tiene permisos de administrador
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return decorated_function


@views.route('/', methods=['GET'])
def home():
    return render_template("home.html", user=current_user, users= User.query.all(), winrates=top_10_winrates(), games = Games.query.filter(Games.created_at >= '2024-01-01').order_by(Games.created_at.desc()).all())


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        photo = request.files["photo"]
        updated = False
        if email != current_user.email and email:
            current_user.email = email
            updated = True
        if name != current_user.first_name and name:
            current_user.first_name = name
            updated = True
        if photo.filename:
            photo_name = secure_filename(photo.filename)
            ruta_carpeta = os. getcwd()+"/website/static/images/"+str(current_user.id)
            os.makedirs(ruta_carpeta, exist_ok=True)
            photo.save(os.path.join(ruta_carpeta, photo_name))
            current_user.photo = photo.filename
            updated = True
        if password1 != password2 and password1:
            flash('El password no coincide.', category='error')
        elif password1 and len(password1) < 4:
            flash('Password must be at least 4 characters.', category='error')
        elif password1:
            current_user.password = generate_password_hash(
                password1, method='sha256')
            updated = True
        if updated:
            message = {'message': '¡Actualizado con éxito!',
                       'category': 'success'}
        else:
            message = {'message': 'No se ha modificado ningún campo',
                       'category': 'error'}

        flash(**message)
        db.session.commit()

    return render_template("profile.html", user=current_user)


@views.route('/dashboard', methods=['GET', 'POST'])
@admin_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@views.route('/dashboard/games', methods=['GET', 'POST'])
@admin_required
def games():
    games = Games.query.order_by(Games.created_at.desc()).all()
    return render_template('games.html', user=current_user, games=games, users=User.query.all())


@views.route('/delete-round', methods=['POST'])
@admin_required
def delete_round():
    # this function expects a JSON from the INDEX.js file
    rounds = json.loads(request.data)
    roundsId = rounds['roundsId']
    rounds = Rounds.query.get(roundsId)
    db.session.delete(rounds)
    db.session.commit()

    return jsonify({})


@views.route('/update-round', methods=['POST'])
@admin_required
def update_round():

    players = request.form.getlist('players')
    round = request.form.get('roundsId')
    victory = request.form.get('victory')
    round = Rounds.query.get(round)
    round.victory = int(victory)
    round.players.clear()
    for player in players:
        round.players.append(User.query.get(player))
    db.session.commit()

    return redirect("/dashboard/games")


@views.route('/add-round', methods=['POST'])
@admin_required
def add_round():

    players = request.form.getlist('players')
    victory = request.form.get('victory') == 'True'
    game_id = request.form.get('game_id')
    last_round = Rounds.query.filter_by(
        game_number=game_id).order_by(Rounds.number.desc()).first()
    new_round_number = last_round.number + 1 if last_round else 1
    new_round = Rounds(number=new_round_number,
                       victory=victory, game_number=game_id)

    for player in players:
        player = User.query.get(player)
        new_round.players.append(player)

    db.session.add(new_round)
    db.session.commit()

    return redirect("/dashboard/games")

@views.route('/update-game', methods=['POST'])
@admin_required
def update_game():
    game_id = request.form.get('game_id')
    game = Games.query.get(game_id)
    place = request.form.get('place') 
    game.position = int(request.form.get('position')) if request.form.get('position') else None
    price = request.form.get('price')
    game.created_at = request.form.get('created_at')

    if place != "":
        game.place = place

    if price != "":
        game.price = price

    db.session.commit()

    return redirect("/dashboard/games")


@views.route('/add-game', methods=['POST'])
@admin_required
def add_game():

    place = request.form.getlist('place')
    position = int(request.form.get('position')) if request.form.get('position') else None
    price = request.form.get('price')
    created_at = request.form.get('created_at')
    print(current_user.id)

    new_game = (Games(place=place, position=position, price=price, created_at=created_at, created_by=current_user.id))

    db.session.add(new_game)
    db.session.commit()

    return redirect("/dashboard/games")


@views.route('/delete-game', methods=['POST'])
@admin_required
def delete_game():
    # this function expects a JSON from the INDEX.js file
    game = json.loads(request.data)
    gameId = game['gameId']
    game = Games.query.get(gameId)
    db.session.delete(game)
    db.session.commit()

    return jsonify({})


@views.route('dashboard/edit-users', methods=['GET', 'POST'])
@admin_required
def edit_users():
    user = None
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user_id = request.form.get('userId')
        user = User.query.get(user_id)
        photo = request.files["photo"]
        updated = False
        if user.is_admin and user is not current_user:
            message = {'message': '¡No puedes modificar otro Admin!',
                       'category': 'error'}
        else:
            if email != user.email and email:
                user.email = email
                updated = True
            if name != user.first_name and name:
                user.first_name = name
                updated = True
            if photo.filename:
                photo_name = secure_filename(photo.filename)
                ruta_carpeta = os. getcwd()+"/website/static/images/"+str(user.id)
                os.makedirs(ruta_carpeta, exist_ok=True)
                photo.save(os.path.join(ruta_carpeta, photo_name))
                user.photo = photo.filename
                updated = True
            if password1 != password2 and password1:
                flash('El password no coincide.', category='error')
            elif password1 and len(password1) < 4:
                flash('Password must be at least 4 characters.', category='error')
            elif password1:
                user.password = generate_password_hash(
                    password1, method='sha256')
                updated = True
            if updated:
                message = {'message': '¡Actualizado con éxito!',
                        'category': 'success'}
            else:
                message = {'message': 'No se ha modificado ningún campo',
                        'category': 'error'}

        flash(**message)
        db.session.commit()
        return render_template("edit_users.html", user_to_edit=user, current_user=current_user, users=User.query.all())
    if not user:
        user_to_edit = current_user
    return render_template("edit_users.html", user_to_edit=user_to_edit, current_user=current_user, users=User.query.all())


@views.route('/user/<int:user_id>/data')
def get_user_data(user_id, year=None):
    year = request.args.get('year')
    user = User.query.get(user_id)
    games_played=[]
    for round in user.rounds_played:
        game = round.game
        if year:
            # Verifica si la fecha de la partida es del año especificado
            if game.created_at.year == int(year):
                if game not in games_played:
                    games_played.append(game)
        else:
            if game not in games_played:
                games_played.append(game)
    
    if current_user.is_admin or current_user.id == user_id:
        data = {
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'photo': user.photo,
            'game_played': [{
                'id':game.id,
                'place': game.place
            } for game in games_played]
            # Agrega otros campos de usuario si es necesario
        }
    else:
        data = {
            'user_id':user.id,
            'first_name':user.first_name,
            'photo': user.photo,
            'game_played': [{
                'id':game.id,
                'place': game.place
            } for game in games_played]
        }
    return jsonify(data)

@views.route('/all-players', methods=['GET'])
def all_players():
    return render_template("all_players.html", user=current_user, users= User.query.all(), winrates=all_users_by_winrate(), games = Games.query.all())

@views.route('/all-tournaments', methods=['GET'])
def all_torunaments():
    return render_template("all_tournaments.html", user=current_user, users= User.query.all(), games = Games.query.order_by(Games.created_at.desc()).all())
