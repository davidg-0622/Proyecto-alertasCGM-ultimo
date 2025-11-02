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
        error = None
        
        # Validar datos
        user = User.query.filter_by(username=username).first()
        
        if user is None:
            error = 'El usuario no existe'
        elif not check_password_hash(user.password, password): 
            error = 'Contraseña incorrecta'
        # AÑADIMOS ESTA VALIDACIÓN:
        elif user.estado == 0: 
            error = 'Usuario inactivo. Valide con el administrador.'
        if error is None:
            session.clear()
            session['user_id'] = user.id_usuario
            return redirect(url_for('app.listar'))   
        
        # Si hay un error (incluido el estado inactivo), se muestra el mensaje flash.
        flash(error)
            
    return render_template('auth/login.html')






############################ Registro #########################

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        estado = 0 
        perfil = request.form['perfil']

        error=None
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            new_user = User(nombre=nombre,apellido=apellido, username=username, email=email, password=generate_password_hash(password),estado=estado, perfil=perfil)
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
    return redirect(url_for('auth.login'))   

######################### Decorador para proteger rutas #########################
def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


################################ Admin ###############################3
@bp.route('/admin', methods=['POST','GET'])
@login_required
def Admin():
    usuarios= User.query.all()
    print(f'los usuarios de la tabla son {usuarios}')
    
    return render_template('admin/usuarios_admin.html', usuarios=usuarios)

################################ Admin- cambiar estado al usuario ###############################3

@bp.route('/cambiar_estado/<int:id_usuario>/<int:nuevo_estado>', methods=['POST', 'GET'])
@login_required
def cambiar_estado(id_usuario, nuevo_estado):
    usuario = User.query.get_or_404(id_usuario)
    
   
    if nuevo_estado in [0, 1]: 
        usuario.estado = nuevo_estado
        db.session.commit()
       
        flash(f'El estado del usuario {usuario.username} ha sido actualizado.', 'success') 
    else:
        flash('Estado no válido.', 'danger')

    # Redirige de vuelta a la página de administración
    return redirect(url_for('auth.Admin'))









