from .. import db



class Alerta(db.Model):
    __tablename__ = 'alertas'

    idalertas = db.Column(db.Integer, primary_key=True)
    Host = db.Column(db.String(100))
    Time = db.Column(db.String(100))
    Recovery_time = db.Column("Recovery time", db.String(100))  # ← con espacio
    Duracion = db.Column(db.Float)
    Status = db.Column(db.String(45))
    Problem = db.Column(db.String(500))
    Ack = db.Column(db.Integer)
    Servicio = db.Column(db.String(500))
    Cod_App = db.Column(db.String(45))
    Tipo = db.Column(db.String(45))
    Rango_Duracion = db.Column("Rango Duracion", db.String(45))  # ← con espacio
    Severity = db.Column(db.String(45))
    Actions = db.Column(db.String(45))
    Tags = db.Column(db.String(800))
    Operational_data = db.Column("Operational data", db.String(800))  # ← con espacio
    Tipo_Servicio = db.Column(db.String(45))

    def __init__(self, idalertas, Host, Time, Recovery_time, Duracion, Status, Problem,
                 Ack, Servicio, Cod_App, Tipo, Rango_Duracion, Severity, Actions,
                 Tags, Operational_data, Tipo_Servicio):
        self.idalertas = idalertas
        self.Host = Host
        self.Time = Time
        self.Recovery_time = Recovery_time
        self.Duracion = Duracion
        self.Status = Status
        self.Problem = Problem
        self.Ack = Ack
        self.Servicio = Servicio
        self.Cod_App = Cod_App
        self.Tipo = Tipo
        self.Rango_Duracion = Rango_Duracion
        self.Severity = Severity
        self.Actions = Actions
        self.Tags = Tags
        self.Operational_data = Operational_data
        self.Tipo_Servicio = Tipo_Servicio

        