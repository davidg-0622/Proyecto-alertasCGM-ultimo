from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from app.models.alertas import Alerta
from app.models.servicio import Servicio     
import pandas as pd



# Define el blueprint una sola vez
bp = Blueprint('alertas', __name__, url_prefix='/alertas')


@bp.route('/')
def total_alertas():
    # Total de alertas
    alertas = db.session.query(Alerta).count()

    # Parámetros de búsqueda y paginación
    label = request.args.get('label', '').strip()
    page = request.args.get('page', 1, type=int)

    # Consulta base
    query = db.session.query(Servicio)

    # Filtro por nombre de servicio
    if label:
        query = query.filter(
            Servicio.servicio.ilike(f'%{label}%') | Servicio.encargado_cgm.ilike(f'%{label}%')
        )

    # Total de servicios encontrados en la búsqueda
    total_servicios = query.count()
   

    # Lógica para per_pages
    if label:
        per_page = total_servicios if total_servicios > 0 else 1
    else:
        per_page = 1

    # Paginación
    servicios_info = query.paginate(page=page, per_page=per_page)


    # Top servicios con más alertas
    top_servicios = (
        db.session.query(Alerta.Servicio, db.func.count().label('total_alertas'))
        .group_by(Alerta.Servicio)
        .order_by(db.desc('total_alertas'))
        .limit(20)
        .all()
    )

    return render_template(
        'alertas/alertas_principal.html',
        alertas=alertas,
        servicios=top_servicios,
        servicios_info=servicios_info,
        label=label,
        per_page=per_page,
        total_servicios=total_servicios
    )



###################################alertas por servicio######################
@bp.route('/alertas_por_servicio')
def alertas_por_servicio():
    servicio = request.args.get('servicio', '').strip()
    severidad = request.args.get('severidad', '').strip()
    fecha_inicio = request.args.get('fecha_inicio', '').strip()
    fecha_fin = request.args.get('fecha_fin', '').strip()

    # Obtener todas las alertas desde la base de datos
    alertas = Alerta.query.all()

    # Convertir a DataFrame
    df_alerts = pd.DataFrame([a.__dict__ for a in alertas])
    df_alerts.drop('_sa_instance_state', axis=1, inplace=True)

    # Convertir columna 'Time' a datetime
    df_alerts['Time'] = pd.to_datetime(df_alerts['Time'], errors='coerce', format='%d/%m/%Y %H:%M')

    # Aplicar filtros
    if servicio:
        df_alerts = df_alerts[df_alerts['Servicio'].str.contains(servicio, case=False, na=False)]
    if severidad:
        df_alerts = df_alerts[df_alerts['Severity'].str.contains(severidad, case=False, na=False)]
    if fecha_inicio:
        try:
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            df_alerts = df_alerts[df_alerts['Time'] >= fecha_inicio_dt]
        except:
            pass
    if fecha_fin:
        try:
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            df_alerts = df_alerts[df_alerts['Time'] <= fecha_fin_dt]
        except:
            pass

    # Conteo de alertas por servicio
    conteo_por_servicio = df_alerts['Servicio'].value_counts().reset_index()
    conteo_por_servicio.columns = ['Servicio', 'Total_Alertas']

    return render_template('alertas/alertas_x_servicio.html', alertas=df_alerts.to_dict(orient='records'),
        conteo_servicios=conteo_por_servicio.to_dict(orient='records')

    )

###################################Detalle alertas ####################

@bp.route('/detalle_alertas')
def detalle_alertas():
    from flask import request, render_template
    import pandas as pd

    # Obtener parámetros de la URL
    servicio = request.args.get('servicio', '').strip()
    severidad = request.args.get('severidad', '').strip()
    fecha_inicio = request.args.get('fecha_inicio', '').strip()
    fecha_fin = request.args.get('fecha_fin', '').strip()

    # Obtener todas las alertas desde la base de datos
    alertas = Alerta.query.all()

    # Convertir a DataFrame
    df_alerts = pd.DataFrame([a.__dict__ for a in alertas])
    df_alerts.drop('_sa_instance_state', axis=1, inplace=True)

    # Renombrar columnas para que coincidan con la plantilla
    df_alerts.rename(columns={
        'servicio': 'Servicio',
        'alerta': 'Alerta',
        'severity': 'Severidad',
        'time': 'Time'
    }, inplace=True)

    # Convertir columna 'Time' a datetime
    df_alerts['Time'] = pd.to_datetime(df_alerts['Time'], errors='coerce', format='%d/%m/%Y %H:%M')

    # Aplicar filtros
    if servicio:
        df_alerts = df_alerts[df_alerts['Servicio'].str.contains(servicio, case=False, na=False)]
    if severidad:
        df_alerts = df_alerts[df_alerts['Severidad'].str.contains(severidad, case=False, na=False)]
    if fecha_inicio:
        try:
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            df_alerts = df_alerts[df_alerts['Time'] >= fecha_inicio_dt]
        except:
            pass
    if fecha_fin:
        try:
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            df_alerts = df_alerts[df_alerts['Time'] <= fecha_fin_dt]
        except:
            pass

    # Crear columna formateada para mostrar en HTML
    df_alerts['Fecha_Hora'] = df_alerts['Time'].dt.strftime('%d/%m/%Y %H:%M')

    # Agrupar por día para el gráfico
    df_alerts['Fecha'] = df_alerts['Time'].dt.date
    conteo_por_dia = df_alerts.groupby('Fecha').size().reset_index(name='Cantidad_Alertas')
    grafico_data = conteo_por_dia.to_dict(orient='records')

    # Renderizar plantilla con alertas filtradas y datos del gráfico
    return render_template(
        'alertas/detalle_alertas.html',
        alertas=df_alerts.to_dict(orient='records'),
        grafico_data=grafico_data
    )