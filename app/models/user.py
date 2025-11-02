from .. import db

class User(db.Model):
    __tablename__ = 'users'  # Usar el atributo __tablename__
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), unique=True, nullable=False)
    apellido = db.Column(db.String(250), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.String(10), default=0, nullable=False)
    perfil = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self,nombre, apellido,  username, email, password, estado, perfil ):
        self.nombre=nombre
        self.apellido=apellido
        self.username = username
        self.email = email
        self.password = password
        self.estado=estado
        self.perfil=perfil
       

    def __repr__(self):
        return f'<User {self.username}>'

