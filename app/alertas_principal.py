from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from app.models.alertas import Alerta
from app.models.servicio import Servicio     
import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import func
from app.auth import login_required




# Define el blueprint una sola vez
bp = Blueprint('alertas', __name__, url_prefix='/alertas')




###################################   Detalle alertas   ####################

###################################   Detalle alertas  - me muestra las cantidad de alertas por clouwash y dynatrace y mas  ####################

@bp.route('/detalle_alertas', methods=['GET', 'POST'])
@login_required
def detalle_alertas():
    # Obtener parámetros de la URL
    servicio_param = request.args.get('servicio', '').strip() 
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()
    host_param = request.args.get('Host', '').strip() 
    operational_data_param = request.args.get('Operational_data', '').strip() 
    rango_duracion_param = request.args.get('Rango_Duracion', '').strip() 


    print(f"DEBUG: Fecha Inicio String: '{fecha_inicio_str}'")
    print(f"DEBUG: Fecha Fin String: '{fecha_fin_str}'")

    # Iniciar la consulta base de SQLAlchemy
    query_alertas = Alerta.query

    # Convertir fechas y aplicar filtros
    fecha_inicio = None
    fecha_fin = None
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            query_alertas = query_alertas.filter(Alerta.time >= fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            # Esta lógica ya es correcta para incluir todo el día final
            fecha_fin_ajustada = fecha_fin + timedelta(days=1) 
            query_alertas = query_alertas.filter(Alerta.time < fecha_fin_ajustada)
        except ValueError:
            pass
    
    # --- CORRECCIÓN CLAVE: Verificar si el parámetro no es la cadena literal "None" ---

    if servicio_param and servicio_param != 'None':
        query_alertas = query_alertas.filter(Alerta.servicio == servicio_param)
    
    if operational_data_param and operational_data_param != 'None':
        query_alertas = query_alertas.filter(Alerta.operational_data.ilike(f'%{operational_data_param}%'))
        
    if host_param and host_param != 'None':
        query_alertas = query_alertas.filter(Alerta.host.ilike(f'%{host_param}%'))
        
    if rango_duracion_param and rango_duracion_param != 'None':
        query_alertas = query_alertas.filter(Alerta.rango_duracion == rango_duracion_param)

    # **Optimización Opcional**: Puedes ordenar directamente con SQLAlchemy antes de pasarlo a Pandas
    query_alertas = query_alertas.order_by(Alerta.time.desc())

    # Obtener las alertas filtradas
    alertas_filtradas = query_alertas.all()

    # Usar Pandas con los datos ya filtrados
    df_alerts = pd.DataFrame([a.__dict__ for a in alertas_filtradas])
    if '_sa_instance_state' in df_alerts.columns:
        df_alerts.drop('_sa_instance_state', axis=1, inplace=True)
    
    # Renombrar columnas para que coincidan con la plantilla (Si tu modelo usa minúsculas, esto es necesario para la plantilla)
    df_alerts.rename(columns={
        'servicio': 'Servicio',
        'time': 'Time',
        'host': 'Host',
        'operational_data': 'Operational_data',
        'rango_duracion': 'Rango_Duracion'
    }, inplace=True)

    # Crear columna formateada para mostrar en HTML
    if 'Time' in df_alerts.columns:
        df_alerts['Fecha_Hora'] = df_alerts['Time'].dt.strftime('%d/%m/%Y %H:%M')
        df_alerts['Fecha'] = df_alerts['Time'].dt.date
        conteo_por_dia = df_alerts.groupby('Fecha').size().reset_index(name='Cantidad_Alertas')
        grafico_data = conteo_por_dia.to_dict(orient='records')
    else:
        grafico_data = []

    # Conteo de hosts y rango de duración
    conteo_hosts = df_alerts['Host'].value_counts().to_dict() if 'Host' in df_alerts.columns else {}
    conteo_rango_duracion = df_alerts['Rango_Duracion'].value_counts().to_dict() if 'Rango_Duracion' in df_alerts.columns else {}

    # Renderizar plantilla con alertas filtradas y datos del gráfico
    return render_template(
        'alertas/detalle_alertas.html',
        alertas=df_alerts.to_dict(orient='records'), # Aquí se pasan los registros ya ordenados
        grafico_data=grafico_data, 
        Host=host_param, 
        conteo_hosts=conteo_hosts,
        conteo_rango_duracion=conteo_rango_duracion,
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str,
        servicios={'Servicio': servicio_param} 
    )


###################################   Total alertas   ####################



###################################   Total alertas   ####################

@bp.route('/', methods=['GET', 'POST'])
@login_required
def total_alertas():
    fecha_inicial = None
    # Cambiamos 'fecha_final' por 'fecha_final_dt' para la consulta
    fecha_final_dt = None 
    label = request.args.get('label', '').strip()
    page = request.args.get('page', 1, type=int)

    # Variables para mantener el estado del formulario en la plantilla
    fecha_inicial_str_form = request.form.get('Fecha_inicial', '')
    fecha_final_str_form = request.form.get('Fecha_final', '')

    if request.method == 'POST':
        fecha_inicial_str = request.form.get('Fecha_inicial')
        fecha_final_str = request.form.get('Fecha_final')

        if fecha_inicial_str and fecha_final_str:
            fecha_inicial = datetime.strptime(fecha_inicial_str, '%Y-%m-%d')
            fecha_final_form = datetime.strptime(fecha_final_str, '%Y-%m-%d')
            
            # --- SOLUCIÓN: Sumamos un día para incluir el día completo ---
            fecha_final_dt = fecha_final_form + timedelta(days=1)
            


    # --- Consultas SQLAlchemy ---
    
    query_top_servicios = db.session.query(
        Alerta.servicio, 
        db.func.count(Alerta.id).label('total_alertas') 
    ).group_by(Alerta.servicio) 

    if fecha_inicial and fecha_final_dt: # Usamos fecha_final_dt
        query_top_servicios = query_top_servicios.filter(
            Alerta.time >= fecha_inicial,
            Alerta.time < fecha_final_dt # Rango excluyente corregido
        )
    
    top_servicios = query_top_servicios.order_by(
        db.desc('total_alertas')
    ).limit(20).all()

    query_total_alertas = db.session.query(Alerta)
    if fecha_inicial and fecha_final_dt: # Usamos fecha_final_dt
        query_total_alertas = query_total_alertas.filter(
            Alerta.time >= fecha_inicial,
            Alerta.time < fecha_final_dt # Rango excluyente corregido
        )
    alertas_total = query_total_alertas.count()
    print(f"Total alertas encontradas: {alertas_total}")

    # --- Paginación ---
    query_servicios = db.session.query(Servicio)
    if label:
        query_servicios = query_servicios.filter(
            Servicio.servicio.ilike(f'%{label}%') | Servicio.encargado_cgm.ilike(f'%{label}%')
        )
    total_servicios = query_servicios.count()
    per_page = total_servicios if label and total_servicios > 0 else (1 if not label else 1) 
    servicios_info = query_servicios.paginate(page=page, per_page=per_page)


    return render_template(
        'alertas/alertas_principal.html',
        alertas=alertas_total,
        servicios=top_servicios,
        servicios_info=servicios_info,
        label=label,
        per_page=per_page,
        total_servicios=total_servicios,
        fecha_inicial_str=fecha_inicial_str_form, 
        fecha_final_str=fecha_final_str_form
    )


###################################   Alertas por servicio   ####################

@bp.route('/alertas_por_servicio', methods=['GET', 'POST'])
@login_required
def alertas_por_servicio():
    servicio = request.args.get('servicio', '').strip()
    severidad = request.args.get('severidad', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()

    # ELIMINA esta línea de aquí: entregado_cgm = db.Column(...) -> NO VA EN LA RUTA

    def aplicar_filtros(q):
        if servicio:
            q = q.filter(Alerta.servicio.ilike(f'%{servicio}%'))
        if severidad:
            q = q.filter(Alerta.severity.ilike(f'%{severidad}%'))
        if fecha_inicio_str:
            try:
                f_ini = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                q = q.filter(Alerta.time >= f_ini)
            except ValueError: pass
        if fecha_fin_str:
            try:
                f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)
                q = q.filter(Alerta.time < f_fin)
            except ValueError: pass
        return q

    # CONSULTA 1: Solo columnas que EXISTEN en tu clase Alerta
    # He quitado Alerta.entregado_cgm para evitar el AttributeError
    query_datos = db.session.query(
        Alerta.id, Alerta.time, Alerta.host, Alerta.servicio, 
        Alerta.severity, Alerta.operational_data
    )
    
    query_datos = aplicar_filtros(query_datos)
    alertas_raw = query_datos.all()
    alertas_list = [r._asdict() for r in alertas_raw]

    # CONSULTA 2: Conteo agrupado
    query_conteo = db.session.query(
        Alerta.servicio.label('Servicio'), 
        func.count(Alerta.id).label('Total_Alertas')
    ).group_by(Alerta.servicio).order_by(func.count(Alerta.id).desc())
    
    query_conteo = aplicar_filtros(query_conteo)
    conteo_servicios = [r._asdict() for r in query_conteo.all()]

    return render_template(
        'alertas/alertas_x_servicio.html', 
        alertas=alertas_list,
        conteo_servicios=conteo_servicios,
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str
    )


################################### Conteo alertas iguales ####################

@bp.route('/conteo_alertas_iguales', methods=['GET'])
@login_required 
def conteo_alertas_iguales():
    servicio_param = request.args.get('servicio', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()
    operational_data_param = request.args.get('operational_data', '').strip()
    rango_duracion_param = request.args.get('Rango_Duracion', '').strip()

    # 1. Optimización: Obtener servicios con un query más directo
    servicios_disponibles = [
        s[0] for s in db.session.query(Alerta.servicio).distinct().order_by(Alerta.servicio).all()
    ]

    # 2. Iniciar consulta SELECT servicio, operational_data, COUNT(*)
    # Esto reemplaza a Pandas y es mucho más rápido
    query_conteo = db.session.query(
        Alerta.servicio, 
        Alerta.operational_data, 
        func.count(Alerta.id).label('cantidad')
    ).group_by(Alerta.servicio, Alerta.operational_data)

    # 3. Aplicar filtros directamente al query de agregación
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            query_conteo = query_conteo.filter(Alerta.time >= fecha_inicio)
        except ValueError: pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)
            query_conteo = query_conteo.filter(Alerta.time < fecha_fin)
        except ValueError: pass
    
    if servicio_param and servicio_param != 'None':
        query_conteo = query_conteo.filter(Alerta.servicio == servicio_param)
    
    if operational_data_param and operational_data_param != 'None':
        query_conteo = query_conteo.filter(Alerta.operational_data.ilike(f'%{operational_data_param}%'))
   
    if rango_duracion_param and rango_duracion_param != 'None':
        query_conteo = query_conteo.filter(Alerta.rango_duracion == rango_duracion_param)

    # 4. Ordenar por cantidad descendente y ejecutar
    # Ahora solo descargas el resumen, no los 79,000 registros
    conteo_resultado = query_conteo.order_by(func.count(Alerta.id).desc()).all()

    # Convertir a formato lista de diccionarios para el template
    conteo = [
        {'servicio': r.servicio, 'operational_data': r.operational_data, 'cantidad': r.cantidad} 
        for r in conteo_resultado
    ]
    
    return render_template(
        'alertas/conteo_alertas_iguales.html', 
        conteo_por_servicio_y_alerta=conteo,  
        servicios_disponibles=servicios_disponibles
    )
