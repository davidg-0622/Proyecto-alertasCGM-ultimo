from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/coes'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)

    # Registrar Blueprints
    from .app import bp as main_bp
    from .auth import bp as auth_bp
    from .boca import bp as boca_bp
    from .alertas_principal import bp as alertas_bp
    from .jobs import bp as jobs_bp  # Importar el Blueprint de jobs

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(alertas_bp)
    app.register_blueprint(boca_bp)
    app.register_blueprint(jobs_bp)  # Registrar el Blueprint de jobs

    # Migra todos los modelos a la base de datos
    with app.app_context():
        db.create_all()  # Crear las tablas en la base de datos

    return app


