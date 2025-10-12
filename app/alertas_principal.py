from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from app.models.alertas import Alerta
from app.models.servicio import Servicio     
import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import func




# Define el blueprint una sola vez
bp = Blueprint('alertas', __name__, url_prefix='/alertas')


@bp.route('/', methods=['GET', 'POST'])
def total_alertas():
    # Inicializa las variables
    fecha_inicial = None
    fecha_final = None
    label = request.args.get('label', '').strip()
    page = request.args.get('page', 1, type=int)

    # Procesa los datos del formulario si es un POST
    if request.method == 'POST':
        fecha_inicial_str = request.form.get('Fecha_inicial')
        fecha_final_str = request.form.get('Fecha_final')

        # Si los datos de fecha existen, conviértelos a objetos datetime
        if fecha_inicial_str and fecha_final_str:
            fecha_inicial = datetime.strptime(fecha_inicial_str, '%Y-%m-%d')
            fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d')
            # Ajusta la fecha final para incluir todo el día
            fecha_final = fecha_final + timedelta(days=1)
    
    # Consulta para el conteo de alertas por servicio, aplicando el filtro de fecha
    query_top_servicios = db.session.query(Alerta.Servicio,db.func.count(Alerta.idalertas).label('total_alertas')).group_by(Alerta.Servicio)

    # Aplica el filtro de fechas a la consulta de conteo si se proporcionaron
    if fecha_inicial and fecha_final:
        query_top_servicios = query_top_servicios.filter(
            func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') >= fecha_inicial,
            func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') < fecha_final
        )
    
    # Ordena y limita los resultados para obtener los top servicios
    top_servicios = query_top_servicios.order_by(
        db.desc('total_alertas')
    ).limit(20).all()

    # Total de alertas, aplicando el mismo filtro de fecha
    query_total_alertas = db.session.query(Alerta)
    if fecha_inicial and fecha_final:
        query_total_alertas = query_total_alertas.filter(
            func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') >= fecha_inicial,
            func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') < fecha_final
        )
    alertas_total = query_total_alertas.count()

    print(f'El total de alertas es: {alertas_total}')


    # Consulta para la paginación de servicios
    query_servicios = db.session.query(Servicio)
    if label:
        query_servicios = query_servicios.filter(
            Servicio.servicio.ilike(f'%{label}%') | Servicio.encargado_cgm.ilike(f'%{label}%')
        )
    total_servicios = query_servicios.count()
    per_page = total_servicios if label and total_servicios > 0 else 1
    servicios_info = query_servicios.paginate(page=page, per_page=per_page)

    print(f'la fecha inicial es: {fecha_inicial} y la fecha final es {fecha_final}')

    return render_template(
        'alertas/alertas_principal.html',
        alertas=alertas_total,
        servicios=top_servicios,
        servicios_info=servicios_info,
        label=label,
        per_page=per_page,
        total_servicios=total_servicios,
        fecha_inicial=fecha_inicial,
        fecha_final=fecha_final - timedelta(days=1) if fecha_final else None
      
    )



###################################alertas por servicio######################

@bp.route('/alertas_por_servicio', methods=['GET', 'POST'])
def alertas_por_servicio():
    servicio = request.args.get('servicio', '').strip()
    severidad = request.args.get('severidad', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()

    # Inicia la consulta base
    query_alertas = Alerta.query

    # Convertir las fechas si existen
    fecha_inicio = None
    fecha_fin = None
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        except ValueError:
            pass
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        except ValueError:
            pass

    # Aplicar filtros a la consulta de SQLAlchemy
    if servicio:
        query_alertas = query_alertas.filter(Alerta.Servicio.ilike(f'%{servicio}%'))
    if severidad:
        query_alertas = query_alertas.filter(Alerta.Severity.ilike(f'%{severidad}%'))
    if fecha_inicio:
        query_alertas = query_alertas.filter(func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') >= fecha_inicio)
    if fecha_fin:
        # Sumar un día a la fecha fin para incluir todo el día
        fecha_fin_ajustada = fecha_fin + timedelta(days=1)
        query_alertas = query_alertas.filter(func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') < fecha_fin_ajustada)

    # Ejecutar la consulta para obtener las alertas filtradas
    alertas = query_alertas.all()

    # Si aún necesitas usar Pandas para el conteo (opción B), el resto del código es igual:
    df_alerts = pd.DataFrame([a.__dict__ for a in alertas])
    if '_sa_instance_state' in df_alerts.columns:
      df_alerts.drop('_sa_instance_state', axis=1, inplace=True)

    # Conteo de alertas por servicio
    if 'Servicio' in df_alerts.columns:
        conteo_por_servicio = df_alerts['Servicio'].value_counts().reset_index()
        conteo_por_servicio.columns = ['Servicio', 'Total_Alertas']
    else:
        conteo_por_servicio = pd.DataFrame(columns=['Servicio', 'Total_Alertas'])


    return render_template(
        'alertas/alertas_x_servicio.html', 
        alertas=df_alerts.to_dict(orient='records'),
        conteo_servicios=conteo_por_servicio.to_dict(orient='records'),
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str
    )





###################################   Detalle alertas   ####################



@bp.route('/detalle_alertas', methods=['GET', 'POST'])
def detalle_alertas():
    # Obtener parámetros de la URL
    servicio = request.args.get('servicio', '').strip()
    severidad = request.args.get('severidad', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()
    Host = request.args.get('Host', '').strip()
    rango_duracion = request.args.get('Rango_Duracion', '').strip()

    # Iniciar la consulta base de SQLAlchemy
    query_alertas = Alerta.query

    # Convertir fechas y aplicar filtros
    fecha_inicio = None
    fecha_fin = None
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            query_alertas = query_alertas.filter(
                func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') >= fecha_inicio
            )
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            # Sumar un día para incluir todo el último día
            fecha_fin_ajustada = fecha_fin + timedelta(days=1)
            query_alertas = query_alertas.filter(
                func.str_to_date(Alerta.Time, '%d/%m/%Y %H:%i') < fecha_fin_ajustada
            )
        except ValueError:
            pass
    
    # Aplicar el filtro de servicio
    if servicio:
        query_alertas = query_alertas.filter(Alerta.Servicio.ilike(f'%{servicio}%'))
    
    if severidad:
        query_alertas = query_alertas.filter(Alerta.Severity.ilike(f'%{severidad}%'))
    if Host:
        query_alertas = query_alertas.filter(Alerta.Host.ilike(f'%{Host}%'))
    if rango_duracion:
        query_alertas = query_alertas.filter(Alerta.Rango_Duracion == rango_duracion)

    # Obtener las alertas filtradas
    alertas_filtradas = query_alertas.all()

    # Usar Pandas con los datos ya filtrados
    df_alerts = pd.DataFrame([a.__dict__ for a in alertas_filtradas])
    if '_sa_instance_state' in df_alerts.columns:
        df_alerts.drop('_sa_instance_state', axis=1, inplace=True)
    
    # Renombrar columnas para que coincidan con la plantilla
    df_alerts.rename(columns={
        'servicio': 'Servicio',
        'alerta': 'Alerta',
        'severity': 'Severidad',
        'time': 'Time',
        'Host': 'Host'
    }, inplace=True)

    # Crear columna formateada para mostrar en HTML
    if 'Time' in df_alerts.columns:
        df_alerts['Time'] = pd.to_datetime(df_alerts['Time'], errors='coerce', format='%d/%m/%Y %H:%M')
        df_alerts['Fecha_Hora'] = df_alerts['Time'].dt.strftime('%d/%m/%Y %H:%M')
        # Agrupar por día para el gráfico
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
        alertas=df_alerts.to_dict(orient='records'),
        grafico_data=grafico_data, 
        Host=Host,
        conteo_hosts=conteo_hosts,
        conteo_rango_duracion=conteo_rango_duracion,
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str
    )
