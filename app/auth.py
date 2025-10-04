from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash   
from . import db
from .models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')



##################### Autenticacion #########################

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error=None
       #validar datos 
        user= User.query.filter_by(username=username).first()
        if user == None:
            error= f'El usuario no existe'
        elif not check_password_hash(user.password, password): 
            error= f'Contraseña incorrecta'
        if error is None:
            session.clear()
            session['user_id'] = user.id_usuario
            return redirect(url_for('app.listar'))   
        
    

        flash(error)
            # La ejecución continúa al return final, mostrando el formulario con el mensaje.

    return render_template('auth/login.html')





############################ Registro #########################

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        error=None
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            new_user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            error= f'Usuario registrado correctamente'
            return redirect(url_for('auth.login'))
        else:
            error= f'El nombre de usuario ya existe'

        flash(error)
            # La ejecución continúa al return final, mostrando el formulario con el mensaje.

    return render_template('auth/register.html')



################################# Mantener sesion ###################3
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)


######################### Cerrar sesion #########################
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('app.index'))   

######################### Decorador para proteger rutas #########################
def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view




