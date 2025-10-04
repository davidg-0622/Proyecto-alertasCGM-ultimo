from .. import db

class User(db.Model):
    __tablename__ = 'users'  # Usar el atributo __tablename__
    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)

    def __init__(self, username, email, password ):
        self.username = username
        self.email = email
        self.password = password
       

    def __repr__(self):
        return f'<User {self.username}>'

