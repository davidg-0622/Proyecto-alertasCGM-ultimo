from .. import db

class StandBy(db.Model):
    __tablename__ = 'standby'
    
    id_standby = db.Column(db.Integer, primary_key=True)
    
    # CLAVE FORÁNEA: Vincula este registro al servicio_cgm
    # Asume que el nombre de la tabla es 'servicio_cgm' y la columna es 'id_servicio'
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio_cgm.id_servicio'), nullable=False)

    # El resto de columnas de tus datos de Stand By
    mes = db.Column('Mes', db.String(50), nullable=True) # Usamos String para 'text'
    fc = db.Column('FC', db.String(255), nullable=True) 
    fc_celular = db.Column('FC:Celular', db.String(255), nullable=True) 
    fc_producto = db.Column('FC:Producto_Soportado', db.String(255), nullable=True) 
    fc_servicio_ti = db.Column('FC:Servicio_TI', db.String(255), nullable=True) 
    fecha_de_servicio = db.Column('Fecha_de_Servicio', db.DateTime, nullable=True) # Usamos DateTime para 'datetime'
    observaciones = db.Column('Observaciones', db.Text, nullable=True)
    validacion = db.Column('Validación', db.String(255), nullable=True)
    fc_empresa = db.Column('FC:Empresa', db.String(255), nullable=True)
    modificado = db.Column('Modificado', db.DateTime, nullable=True)
    modificado_por = db.Column('Modificado_por', db.String(255), nullable=True)
    creado = db.Column('Creado', db.DateTime, nullable=True)
    creado_por = db.Column('Creado_por', db.String(255), nullable=True)
    tipo_de_elemento = db.Column('Tipo_de_elemento', db.String(255), nullable=True)
    ruta_de_acceso = db.Column('Ruta_de_acceso', db.String(255), nullable=True)
    
    # Columnas numéricas (doble)
    fi1 = db.Column('FI1', db.Float, nullable=True) # Float para 'double'
    ff1 = db.Column('FF1', db.Float, nullable=True)
    fi2 = db.Column('FI2', db.Float, nullable=True)
    ff2 = db.Column('FF2', db.Float, nullable=True)
    fi3 = db.Column('FI3', db.Float, nullable=True)
    ff3 = db.Column('FF3', db.Float, nullable=True)
    fi4 = db.Column('FI4', db.Float, nullable=True)
    ff4 = db.Column('FF4', db.Float, nullable=True)
    valida1 = db.Column('Valida1', db.Float, nullable=True)
    valida2 = db.Column('Valida2', db.Float, nullable=True)
    valida3 = db.Column('Valida3', db.Float, nullable=True)
    valida4 = db.Column('Valida4', db.Float, nullable=True)

 # --- Constructor ( __init__ ) ---
    def __init__(self, servicio_id, mes, fc, fc_celular, fc_producto, fc_servicio_ti, 
                 fecha_de_servicio, observaciones, validacion, fc_empresa, modificado, 
                 modificado_por, creado, creado_por, tipo_de_elemento, ruta_de_acceso, 
                 fi1, ff1, fi2, ff2, fi3, ff3, fi4, ff4, valida1, valida2, valida3, valida4):
        
        self.servicio_id = servicio_id
        self.mes = mes
        self.fc = fc
        self.fc_celular = fc_celular
        self.fc_producto = fc_producto
        self.fc_servicio_ti = fc_servicio_ti
        self.fecha_de_servicio = fecha_de_servicio
        self.observaciones = observaciones
        self.validacion = validacion
        self.fc_empresa = fc_empresa
        self.modificado = modificado
        self.modificado_por = modificado_por
        self.creado = creado
        self.creado_por = creado_por
        self.tipo_de_elemento = tipo_de_elemento
        self.ruta_de_acceso = ruta_de_acceso
        self.fi1 = fi1
        self.ff1 = ff1
        self.fi2 = fi2
        self.ff2 = ff2
        self.fi3 = fi3
        self.ff3 = ff3
        self.fi4 = fi4
        self.ff4 = ff4
        self.valida1 = valida1
        self.valida2 = valida2
        self.valida3 = valida3
        self.valida4 = valida4

    # --- Representación ( __repr__ ) ---
    def __repr__(self):
        return f'<StandBy ID: {self.id_standby}, Mes: {self.mes}, FC: {self.fc}>'

