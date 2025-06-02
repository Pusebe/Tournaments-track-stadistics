from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, make_response
from flask_login import login_required, current_user, login_user
from .models import Games, User, Rounds, Convocation, ConvocationUser, UserDevice
from .sql import *
import json
import math
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
from sqlalchemy import desc, text
from functools import wraps
from .services.onesignal_service import OneSignalService
from .services.telegram_service import TelegramService
from datetime import datetime
import pytz

views = Blueprint('views', __name__)

onesignal_service = OneSignalService()
telegram= TelegramService()


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
    return render_template("home.html", user=current_user, users= User.query.all(), winrates=get_users_by_winrate(2025, 10), games = Games.query.filter(Games.created_at >= '2025-01-01').order_by(Games.created_at.desc()).all())


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
                password1, method='pbkdf2:sha256')
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

    db.session.add(new_round)  # <--- Añadir a la sesión aquí

    for player_id in players:
        player = User.query.get(player_id)
        if player:
            new_round.players.append(player)

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

@views.route('/delete-user', methods=['POST'])
@admin_required
def delete_user():
    # this function expects a JSON from the INDEX.js file
    user = json.loads(request.data)
    userId = user['userId']
    user = User.query.get(userId)
    db.session.delete(user)
    db.session.commit()

    return jsonify({})

@views.route('/dashboard/edit-users', methods=['GET', 'POST'])
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
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash('¡El email ya está en uso por otro usuario!', category='error')
                return render_template("edit_users.html", user=user, current_user=current_user, users=User.query.all())
            else:
                user.email = email
                updated = True
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
                    password1, method='pbkdf2:sha256')
                updated = True
            if updated:
                message = {'message': '¡Actualizado con éxito!',
                        'category': 'success'}
            else:
                message = {'message': 'No se ha modificado ningún campo',
                        'category': 'error'}

        flash(**message)
        db.session.commit()
        return render_template("edit_users.html", user=user, current_user=current_user, users=User.query.all())
    if not user:
        user = current_user
    return render_template("edit_users.html", user=user, current_user=current_user, users=User.query.all())

@views.route('/dashboard/create_users', methods=['POST'])
@admin_required
def create_users():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('El email ya existe', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('El password no coincide.', category='error')
        elif len(password1) < 4:
            flash('Password must be at least 4 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            #login_user(new_user, remember=True)
            flash('Usuario creado con éxito', category='success')
            #return render_template("edit_users.html", user=new_user, current_user=current_user, users=User.query.all())
            return redirect(url_for('views.edit_users'))

   #return render_template("edit_users.html", user=user, current_user=current_user, users=User.query.all())

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
    # Diccionario base con datos comunes a todos los usuarios
    data = {
        'user_id': user.id,
        'first_name': user.first_name,
        'photo': user.photo,
        'game_played': [{
            'id': game.id, 
            'place': game.place} for game in games_played
            ]
    }
    # Comprobar si el usuario está autenticado
    if current_user.is_authenticated and (current_user.is_admin or current_user.id == user_id):
            # Si es admin o usuario actual, agregar email
        data.update({'email': user.email})

    return jsonify(data)

@views.route('/all-players', methods=['GET'])
def all_players():
    return render_template("all_players.html", user=current_user, users= User.query.all(), winrates=get_users_by_winrate(), games = Games.query.all())

@views.route('/all-tournaments', methods=['GET'])
def all_torunaments():
    return render_template("all_tournaments.html", user=current_user, users= User.query.all(), games = Games.query.order_by(Games.created_at.desc()).all())

@views.route('/announcement', methods=['GET', 'POST'])
@admin_required
def create_announcement():
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        date_str = request.form.get('date')  # YYYY-MM-DDTHH:MM
        place = request.form.get('place')
        player_ids = request.form.getlist('players')  # IDs de usuarios seleccionados
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            date = pytz.timezone('Atlantic/Canary').localize(date)

            convocation = Convocation(
                subject=subject,
                date=date,
                place=place,
                created_by=current_user.id
            )
            db.session.add(convocation)
            db.session.flush()  # Obtener ID de convocation

            # Añadir usuarios seleccionados
            for user_id in player_ids:
                user = User.query.get(user_id)
                if user:
                    if not ConvocationUser.query.filter_by(convocation_id=convocation.id, user_id=user.id).first():
                        convocation_user = ConvocationUser(
                            convocation_id=convocation.id,
                            user_id=user_id
                        )
                        db.session.add(convocation_user)

                    # Enviar notificación 
                    devices = UserDevice.query.filter_by(user_id=user_id).all()

                    if devices:
                        player_ids = [device.onesignal_id for device in devices]
                        onesignal_service.send_convocation_notification(
                            convocation, user, player_ids, convocation.token
                        )

            db.session.commit()
            return redirect(url_for('views.create_announcement'))  # Recarga la página
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 400

    users = User.query.all()
    convocations = Convocation.query.order_by(Convocation.created_at.desc()).all()
    
    # Ordenar los usuarios invitados de cada convocatoria
    for convocation in convocations:
        convocation.invited_users.sort(key=lambda cu: (
            not cu.confirmed,  # Confirmados primero
            cu.confirmed_at or datetime.max  # Por fecha de confirmación
        ))
    
    return render_template('create_announcement.html', users=users, convocations=convocations)


@views.route('/convocation', methods=['GET', 'POST'])
def join_convocation():
    token = request.args.get('token')
    convocation = Convocation.query.filter_by(token=token).first()

    if not convocation:
        flash('Convocatoria no encontrada', 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # FILTRO: Ignorar requests que no tengan user_id (requests de OneSignal)
        user_id = request.form.get('user_id')
        if not user_id:
            print("POST request sin user_id - probablemente de OneSignal, ignorando...")
            return '', 204  # No Content - ignora silenciosamente
        
        onesignal_id = request.form.get('onesignal_id')

        user = User.query.get(user_id)
        if not user:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('views.join_convocation', token=token))

        # Registrar dispositivo
        if onesignal_id:
            device = UserDevice.query.filter_by(onesignal_id=onesignal_id, user_id=user.id).first()
            if not device:
                device = UserDevice(user_id=user.id, onesignal_id=onesignal_id)
                db.session.add(device)
                db.session.commit()

        # Confirmar usuario en la convocatoria
        convocation_user = ConvocationUser.query.filter_by(
            convocation_id=convocation.id, user_id=user.id
        ).first()
        if convocation_user:
            convocation_user.confirmed = True
            convocation_user.confirmed_at = datetime.utcnow()
            db.session.commit()
            
            # Telegram para avisar
            mensaje = f"✅ {user.first_name} se ha registrado en: {convocation.subject}"
            telegram.send_message(mensaje)

            # Programar recordatorio
            player_ids = [device.onesignal_id for device in UserDevice.query.filter_by(user_id=user.id).all()]
            onesignal_service.schedule_reminder_notification(convocation, user, player_ids)

            # Notificación a los admin
            onesignal_service.alert_admin(convocation, user, player_ids, token)

            flash('¡Confirmado en la convocatoria exitosamente!', 'success')
            
            # CREAR COOKIE DE CONFIRMACIÓN
            response = make_response(redirect(url_for('views.join_convocation', token=token)))
            
            # Crear cookie simple con datos del usuario
            cookie_data = f"{user_id}:{convocation.id}"
            
            # Configurar cookie (permanente hasta que se sobrescriba)
            response.set_cookie('convocation_confirmed', cookie_data)
            
            return response
        else:
            flash('No estás invitado a esta convocatoria', 'error')
            return redirect(url_for('views.join_convocation', token=token))

    # === LÓGICA PARA GET ===
    detected_user_id = None
    onesignal_id_from_request = request.args.get('onesignal_id')
    
    # PRIORIDAD 1: OneSignal ID (más fiable)
    if onesignal_id_from_request:
        device = UserDevice.query.filter_by(onesignal_id=onesignal_id_from_request).first()
        if device:
            invited_user_ids = [cu.user_id for cu in convocation.invited_users]
            if device.user_id in invited_user_ids:
                detected_user_id = device.user_id

    # PRIORIDAD 2: Cookie de confirmación (si no hay OneSignal)
    if not detected_user_id:
        cookie_value = request.cookies.get('convocation_confirmed')
        if cookie_value:
            try:
                # Cookie simple formato: "user_id:convocation_id"
                parts = cookie_value.split(':')
                if len(parts) == 2:
                    cookie_user_id = int(parts[0])
                    cookie_convocation_id = int(parts[1])
                    
                    # Verificar que la cookie es para esta convocatoria
                    if cookie_convocation_id == convocation.id:
                        # Verificar que el usuario está invitado a esta convocatoria
                        invited_user_ids = [cu.user_id for cu in convocation.invited_users]
                        if cookie_user_id in invited_user_ids:
                            detected_user_id = cookie_user_id
                            print(f"Usuario identificado por cookie: {cookie_user_id}")
                            
            except (ValueError, IndexError) as e:
                print(f"Error al leer cookie: {e}")
                # Cookie inválida, la ignoramos

    # Verificar si el usuario detectado ya confirmó
    user_already_confirmed = False
    user_confirmation_date = None
    if detected_user_id:
        confirmed_user = ConvocationUser.query.filter_by(
            convocation_id=convocation.id, 
            user_id=detected_user_id,
            confirmed=True
        ).first()
        if confirmed_user:
            user_already_confirmed = True
            user_confirmation_date = confirmed_user.confirmed_at

    # SIEMPRE obtener todos los usuarios confirmados
    confirmed_convocation_users = ConvocationUser.query.filter_by(
        convocation_id=convocation.id,
        confirmed=True
    ).all()
    confirmed_users = [cu.user for cu in confirmed_convocation_users]
    
    # Obtener datos del usuario actual (solo si ya está confirmado)
    current_user_name = ""
    current_user_photo = ""
    if user_already_confirmed and detected_user_id:
        current_user = User.query.get(detected_user_id)
        if current_user:
            current_user_name = current_user.first_name
            current_user_photo = current_user.photo

    # Determinar qué usuarios mostrar
    if detected_user_id:
        users = [User.query.get(detected_user_id)]
    else:
        users = [cu.user for cu in convocation.invited_users]

    return render_template('join_convocation.html', 
                         convocation=convocation, 
                         users=users, 
                         detected_user_id=detected_user_id,
                         user_already_confirmed=user_already_confirmed,
                         user_confirmation_date=user_confirmation_date,
                         confirmed_users=confirmed_users,
                         current_user_name=current_user_name,
                         current_user_photo=current_user_photo)

#acortador de rutas
@views.route('/<short_id>')
def redirect_convocation(short_id):
    conv = Convocation.query.filter_by(short_id=short_id).first_or_404()
    return redirect(url_for('views.join_convocation', token=conv.token))


@views.route('/OneSignalSDKWorker.js')
def onesignal_worker():
    return send_from_directory('static', 'OneSignalSDKWorker.js', mimetype='application/javascript')