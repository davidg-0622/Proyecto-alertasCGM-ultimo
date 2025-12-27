from .. import db
from datetime import datetime # Importar datetime no es estrictamente necesario para el modelo en sí

class Alerta(db.Model):
    # En la BD tu tabla se llama 'alertas' (minúsculas, plural)
    # SQLAlchemy lo inferiría automáticamente, pero lo dejamos explícito si quieres 'alertas1'
    __tablename__ = 'alertas1' 

    # --- Definición de Columnas (siguiendo PEP 8: snake_case para atributos Python) ---

    # Mapeo de 'idalertas' a 'id' para mayor claridad y convención
    id = db.Column('idalertas', db.Integer, primary_key=True, autoincrement=True) 
    
    # SQLAlchemy mapea automáticamente atributos a columnas con el mismo nombre
    # Sin embargo, si quieres mantener el nombre de la BD original (capitalizado), 
    # puedes usar el argumento 'name'. Lo haremos para ser precisos con tu tabla original.

    host = db.Column('Host', db.Text) # Usamos db.Text como en tu BD original
    time = db.Column('Time', db.DateTime(timezone=False)) # timezone=False por defecto
    recovery_time_str = db.Column('Recovery_time', db.String(100)) 
    
    # Mapeo de Duracion a duracion, especificando el tipo exacto
    duracion = db.Column('Duracion', db.Double)
    status = db.Column('Status', db.Text)
    problem = db.Column('Problem', db.Text)
    # Usamos db.BigInteger para mapear correctamente el BIGINT de MySQL
    ack = db.Column('Ack', db.BigInteger) 
    servicio = db.Column('Servicio', db.Text)
    cod_app = db.Column('Cod_App', db.Text)
    tipo = db.Column('Tipo', db.Text)
    
    # Estos nombres de columna ya usan guiones bajos, no necesitan el argumento 'name'
    rango_duracion = db.Column('Rango_Duracion', db.Text) 
    severity = db.Column('Severity', db.Text)
    actions = db.Column('Actions', db.Text)
    tags = db.Column('Tags', db.Text)
    
    # Este nombre de columna ya usa guion bajo, no necesita el argumento 'name'
    operational_data = db.Column('Operational_data', db.Text) 
    
    tipo_servicio = db.Column('Tipo_Servicio', db.Text)

    # --- Método __repr__ (recomendado) ---
    
    def __repr__(self):
        """Representación útil al imprimir el objeto Alerta."""
        return f'<Alerta id={self.id} host={self.host!r} status={self.status!r}>'

    # --- Nota sobre __init__ ---
    # SQLAlchemy proporciona un constructor predeterminado que acepta argumentos de palabra clave.
    # El __init__ manual de tu ejemplo no es necesario y a menudo se omite en favor del constructor automático.
    # Puedes crear instancias así: 
    # nueva_alerta = Alerta(Host='servidor1', Status='UP', Time=datetime.now(), ...)
