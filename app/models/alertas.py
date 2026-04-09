from .. import db
from datetime import datetime # Importar datetime no es estrictamente necesario para el modelo en sí


class Alerta(db.Model):
    __tablename__ = 'data_marzo2026' 

    # Identificador principal
    id = db.Column('idalertas', db.Integer, primary_key=True, autoincrement=True) 
    
    # Columnas de Tiempo
    host = db.Column('Host', db.Text)
    time = db.Column('Time', db.DateTime)
    recovery_time = db.Column('Recovery_time', db.DateTime) # Cambiado a DateTime
    
    # Métricas y Estado
    duracion = db.Column('Duracion', db.Text) # Cambiado a Text según tu esquema
    rango_duracion = db.Column('Rango_Duracion', db.Text)
    status = db.Column('Status', db.Text)
    problem = db.Column('Problem', db.Text)
    ack = db.Column('Ack', db.BigInteger) 
    
    # Clasificación y Metadata
    servicio = db.Column('servicio', db.Text)
    cod_app = db.Column('Cod_App', db.Text)
    tipo = db.Column('tipo', db.Text)
    tipo_servicio = db.Column('Tipo_Servicio', db.Text)
    id_entidad = db.Column('id_entidad', db.Text)
    nombre_entidad = db.Column('nombre_entidad', db.Text)
    entregado_cgm = db.Column('entregado_cgm', db.Text) # Agregada
    tipo_problem = db.Column('tipo_problem', db.Text)   # Agregada
    
    # Detalles Técnicos
    tags = db.Column('Tags', db.Text)
    severity = db.Column('Severity', db.Text)
    operational_data = db.Column('Operational_data', db.Text)
    #actions = db.Column('Actions', db.String(45)) # Ajustado a varchar(45)

    def __repr__(self):
        return f'<Alerta id={self.id} host={self.host} problem={self.problem[:20]}...>'
