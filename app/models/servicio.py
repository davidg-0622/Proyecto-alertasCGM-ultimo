from .. import db

class Servicio(db.Model):
    __tablename__ = 'servicio_cgm'
    id_servicio = db.Column(db.Integer, primary_key=True)
    codigo_de_aplicacion = db.Column(db.String(45), nullable=True) # Tu tabla tiene VARCHAR(45)
    servicio=db.Column(db.String(100), nullable=False) # Tu tabla tiene VARCHAR(100)
    descripcion_del_servicio = db.Column(db.String(500), nullable=False) # Tu tabla tiene VARCHAR(500)
    promesa_del_servicio = db.Column(db.String(200), nullable=False) # Tu tabla tiene VARCHAR(200)
    sre = db.Column(db.String(100), nullable=False) # Tu tabla tiene VARCHAR(100)
    evc = db.Column(db.String(100), nullable=False) # Tu tabla tiene VARCHAR(100)
    contacto_del_lider = db.Column(db.Integer, nullable=True) # Tu tabla tiene INT
    po = db.Column(db.String(100), nullable=False) # Tu tabla tiene VARCHAR(100)
    elemento_de_configuracion = db.Column(db.String(45), nullable=True) # Tu tabla tiene VARCHAR(45)
    
    # Mapeo de la columna con espacio
    grupo_inc_helix = db.Column('grupo_ inc_ helix', db.String(250), nullable=False) # Tu tabla tiene VARCHAR(250)
    
    runbook = db.Column(db.String(500), nullable=True) # Tu tabla tiene VARCHAR(500)
    carpeta_servicios_entregados = db.Column(db.String(45), nullable=True) # Tu tabla tiene VARCHAR(45)
    relacion_de_servicios = db.Column('relacion_de_ servicios', db.String(300), nullable=True) # Corregir el espacio
    nombre_grupo_stand_by = db.Column(db.String(200), nullable=True) # Tu tabla tiene VARCHAR(200)
    lider_tecnico_evc = db.Column(db.String(100), nullable=False) # Tu tabla tiene VARCHAR(100)
    lider_linea_area_conocimiento = db.Column(db.String(100), nullable=False) # Tu tabla tiene VARCHAR(100)
    servicio_especial = db.Column(db.String(45), nullable=True) # Tu tabla tiene VARCHAR(45)
    servicio_clave = db.Column(db.String(45), nullable=True) # Tu tabla tiene VARCHAR(45)
    encargado_cgm = db.Column(db.String(250), nullable=True) # Tu tabla tiene VARCHAR(250)
    plataforma=db.Column(db.String(45), nullable=False) # Tu tabla tiene VARCHAR(45)
    
    def __init__(
        self,
        codigo_de_aplicacion,
        servicio, 
        descripcion_del_servicio,
        promesa_del_servicio,
        sre,
        evc,
        contacto_del_lider,
        po,
        elemento_de_configuracion,
        grupo_inc_helix,
        runbook,
        carpeta_servicios_entregados,
        relacion_de_servicios,
        nombre_grupo_stand_by,
        lider_tecnico_evc,
        lider_linea_area_conocimiento,
        encargado_cgm,
        servicio_especial, 
        servicio_clave,
        plataforma
    ):
        self.codigo_de_aplicacion = codigo_de_aplicacion
        self.servicio=servicio
        self.descripcion_del_servicio = descripcion_del_servicio
        self.promesa_del_servicio = promesa_del_servicio
        self.sre = sre
        self.evc = evc
        self.contacto_del_lider = contacto_del_lider
        self.po = po
        self.elemento_de_configuracion = elemento_de_configuracion
        self.grupo_inc_helix = grupo_inc_helix
        self.runbook = runbook
        self.carpeta_servicios_entregados = carpeta_servicios_entregados
        self.relacion_de_servicios = relacion_de_servicios
        self.nombre_grupo_stand_by = nombre_grupo_stand_by
        self.lider_tecnico_evc = lider_tecnico_evc
        self.lider_linea_area_conocimiento = lider_linea_area_conocimiento
        self.servicio_especial=servicio_especial
        self.servicio_clave=servicio_clave
        self.encargado_cgm=encargado_cgm
        self.plataforma=plataforma

    def __repr__(self):
        return f'<servicio {self.id_servicio}>'

