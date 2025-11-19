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

###################################   Total alertas   ####################

@bp.route('/', methods=['GET', 'POST'])
@login_required
def total_alertas():
    fecha_inicial = None
    fecha_final = None
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
            fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d')
            


    # --- Consultas SQLAlchemy ---
    
    query_top_servicios = db.session.query(
        Alerta.servicio, # <--- Corregido al modelo revisado
        db.func.count(Alerta.id).label('total_alertas') # <--- Corregido al modelo revisado
    ).group_by(Alerta.servicio) # <--- Corregido al modelo revisado

    if fecha_inicial and fecha_final:
        query_top_servicios = query_top_servicios.filter(
            Alerta.time >= fecha_inicial,
            Alerta.time < fecha_final # Rango excluyente en el límite superior
        )
    
    top_servicios = query_top_servicios.order_by(
        db.desc('total_alertas')
    ).limit(20).all()

    query_total_alertas = db.session.query(Alerta)
    if fecha_inicial and fecha_final:
        query_total_alertas = query_total_alertas.filter(
            Alerta.time >= fecha_inicial,
            Alerta.time < fecha_final
        )
    alertas_total = query_total_alertas.count()
    print(f"Total alertas encontradas: {alertas_total}")

    # --- Paginación ---
    # ... (tu código de paginación de servicios existente que es correcto) ...
    query_servicios = db.session.query(Servicio)
    if label:
        query_servicios = query_servicios.filter(
            Servicio.servicio.ilike(f'%{label}%') | Servicio.encargado_cgm.ilike(f'%{label}%')
        )
    total_servicios = query_servicios.count()
    # Ajuste para evitar división por cero si no hay resultados
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
        # Pasamos las fechas para que los campos del formulario mantengan su valor
        fecha_inicial_str=fecha_inicial_str_form, 
        fecha_final_str=fecha_final_str_form
    )




###################################alertas por servicio######################


@bp.route('/alertas_por_servicio', methods=['GET', 'POST'])
@login_required
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
        query_alertas = query_alertas.filter(Alerta.servicio.ilike(f'%{servicio}%'))
    if severidad:
        query_alertas = query_alertas.filter(Alerta.severity.ilike(f'%{severidad}%'))
    if fecha_inicio:
        # Usa Alerta.time directamente, ya que es un campo DateTime
        query_alertas = query_alertas.filter(Alerta.time >= fecha_inicio)
    if fecha_fin:
        # Usa Alerta.time directamente, ya que es un campo DateTime
        fecha_fin_ajustada = fecha_fin + timedelta(days=1)
        query_alertas = query_alertas.filter(Alerta.time < fecha_fin_ajustada)

    # Ejecutar la consulta para obtener las alertas filtradas
    alertas = query_alertas.all()

    # Procesar con Pandas
    df_alerts = pd.DataFrame([a.__dict__ for a in alertas])
    print(f'las alertas por servicio es {df_alerts}')
    if '_sa_instance_state' in df_alerts.columns:
      df_alerts.drop('_sa_instance_state', axis=1, inplace=True)


    # Conteo de alertas por servicio
    if 'servicio' in df_alerts.columns: 
        conteo_por_servicio = df_alerts['servicio'].value_counts().reset_index()
        print(conteo_por_servicio.head())  # Depuración: muestra las primeras filas del DataFrame
        conteo_por_servicio.columns = ['Servicio', 'Total_Alertas']
    else:
        conteo_por_servicio = pd.DataFrame(columns=['Servicio', 'Total_Alertas'])

       

    # AHORA SÍ, LA INSTRUCCIÓN RETURN COMPLETA Y SIN COMENTARIOS
    return render_template(
        'alertas/alertas_x_servicio.html', 
        alertas=df_alerts.to_dict(orient='records'),
        conteo_servicios=conteo_por_servicio.to_dict(orient='records'),
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str
    )







###################################   Detalle alertas   ####################

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
            fecha_fin_ajustada = fecha_fin + timedelta(days=1)
            query_alertas = query_alertas.filter(Alerta.time < fecha_fin_ajustada)
        except ValueError:
            pass
    
    # Aplicar el filtro de servicio
    if servicio_param:
        query_alertas = query_alertas.filter(Alerta.servicio == servicio_param)
    
    if operational_data_param:
        query_alertas = query_alertas.filter(Alerta.operational_data.ilike(f'%{operational_data_param}%'))
    if host_param:
        query_alertas = query_alertas.filter(Alerta.host.ilike(f'%{host_param}%'))
    if rango_duracion_param:
        query_alertas = query_alertas.filter(Alerta.rango_duracion == rango_duracion_param)

    # **Optimización Opcional**: Puedes ordenar directamente con SQLAlchemy antes de pasarlo a Pandas
    query_alertas = query_alertas.order_by(Alerta.time.desc())

    # Obtener las alertas filtradas
    alertas_filtradas = query_alertas.all()

    # Usar Pandas con los datos ya filtrados
    df_alerts = pd.DataFrame([a.__dict__ for a in alertas_filtradas])
    if '_sa_instance_state' in df_alerts.columns:
        df_alerts.drop('_sa_instance_state', axis=1, inplace=True)
    
    # Renombrar columnas para que coincidan con la plantilla
    df_alerts.rename(columns={
        'servicio': 'Servicio',
        'time': 'Time',
        'host': 'Host',
        'operational_data': 'Operational_data',
        'rango_duracion': 'Rango_Duracion'
    }, inplace=True)

    # ORDENAR LA LISTA USANDO PANDAS (Si prefieres esta opción en lugar de la de SQLAlchemy)
    # if 'Time' in df_alerts.columns:
    #     df_alerts.sort_values(by='Time', ascending=False, inplace=True)


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


###################################   Conteo alertas iguales   ####################

@bp.route('/conteo_alertas_iguales', methods=['GET'])
@login_required 
def conteo_alertas_iguales():
    servicio = request.args.get('servicio', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()
    operational_data = request.args.get('operational_data', '').strip()
    rango_duracion = request.args.get('Rango_Duracion', '').strip()

    # Obtener todos los servicios únicos para el menú desplegable
    # USAR: Alerta.servicio (minúscula)
    servicios_disponibles = [
        row[0] for row in Alerta.query.with_entities(Alerta.servicio).distinct().order_by(Alerta.servicio).all()
    ]

    # Inicializar la consulta base
    query_alertas = Alerta.query

    # Convertir fechas y aplicar filtros
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            # USAR: Alerta.time (minúscula)
            query_alertas = query_alertas.filter(Alerta.time >= fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            fecha_fin_ajustada = fecha_fin + timedelta(days=1)
            # USAR: Alerta.time (minúscula)
            query_alertas = query_alertas.filter(Alerta.time < fecha_fin_ajustada)
        except ValueError:
            pass
    
    # Aplicar el filtro de servicio
    if servicio:
        # USAR: Alerta.servicio (minúscula)
        query_alertas = query_alertas.filter(Alerta.servicio == servicio)
    
    if operational_data:
        # USAR: Alerta.operational_data (minúscula)
        query_alertas = query_alertas.filter(Alerta.operational_data.ilike(f'%{operational_data}%'))
   
    if rango_duracion:
        # USAR: Alerta.rango_duracion (minúscula)
        query_alertas = query_alertas.filter(Alerta.rango_duracion == rango_duracion)

    # Obtener las alertas filtradas
    alertas_filtradas = query_alertas.all()

    # Convertir las alertas filtradas a un DataFrame de Pandas
    df_alertas_detalladas = pd.DataFrame({
        # USAR: alerta.time, alerta.host, alerta.operational_data, alerta.servicio (minúscula)
        'time': [alerta.time for alerta in alertas_filtradas],
        'host': [alerta.host for alerta in alertas_filtradas],
        'operational_data': [alerta.operational_data for alerta in alertas_filtradas],
        'servicio': [alerta.servicio for alerta in alertas_filtradas],
    })

    # Realizar el conteo de alertas por tipo de 'operational_data' y 'servicio'
    if not df_alertas_detalladas.empty:
        # Usar los nombres de las columnas del DataFrame para el groupby
        conteo_por_servicio_y_alerta_df = df_alertas_detalladas.groupby(['servicio', 'operational_data']).size().reset_index(name='cantidad')
        conteo_lista = conteo_por_servicio_y_alerta_df.to_dict('records')
        conteo = sorted(conteo_lista, key=lambda x: x['cantidad'], reverse=True)
    else:
        conteo = [] 
    
    return render_template(
        'alertas/conteo_alertas_iguales.html', 
        conteo_por_servicio_y_alerta=conteo,  
        servicios_disponibles=servicios_disponibles
    )