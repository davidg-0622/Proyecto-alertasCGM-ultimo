from .. import db


class Job(db.Model):
    __tablename__ = 'data_jobs' 

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True) 
    Subsistema = db.Column('Subsistema', db.Text)
    Nombre_trabajo = db.Column('Nombre_trabajo', db.Text) # Cambiado a Text según tu esquema
    

    def __repr__(self):
        return f'<Job id={self.id} Subsistema={self.Subsistema} Nombre_trabajo={self.Nombre_trabajo[:20]}...>'