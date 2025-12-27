from .. import db

class Servicio(db.Model):
    __tablename__ = 'servicio_cgm'
    
    id_servicio = db.Column(db.Integer, primary_key=True)
    codigo_de_aplicacion = db.Column(db.String(45), nullable=True)
    servicio = db.Column(db.String(100), nullable=False)
    descripcion_del_servicio = db.Column(db.String(500), nullable=False)
    promesa_del_servicio = db.Column(db.String(200), nullable=False)
    sre = db.Column(db.String(100), nullable=False)
    evc = db.Column(db.String(100), nullable=False)
    contacto_del_lider = db.Column(db.Integer, nullable=True)
    po = db.Column(db.String(100), nullable=False)
    elemento_de_configuracion = db.Column(db.String(45), nullable=True)
    
    # Mapeo de columnas con nombres especiales en la DB
    grupo_inc_helix = db.Column('grupo_ inc_ helix', db.String(250), nullable=False)
    relacion_de_servicios = db.Column('relacion_de_ servicios', db.String(300), nullable=True)
    
    runbook = db.Column(db.String(500), nullable=True)
    carpeta_servicios_entregados = db.Column(db.String(45), nullable=True)
    nombre_grupo_stand_by = db.Column(db.String(200), nullable=True)
    lider_tecnico_evc = db.Column(db.String(100), nullable=False)
    lider_linea_area_conocimiento = db.Column(db.String(100), nullable=False)
    servicio_especial = db.Column(db.String(45), nullable=True)
    servicio_clave = db.Column(db.String(45), nullable=True)
    encargado_cgm = db.Column(db.String(250), nullable=True)
    plataforma = db.Column(db.String(45), nullable=False)
    entregado_cgm = db.Column('Entregado_CGM', db.String(45), nullable=True)

    def __init__(self, **kwargs):
        # Usar **kwargs es mucho más limpio y evita errores de comas
        super(Servicio, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Servicio {self.servicio} (ID: {self.id_servicio})>'
