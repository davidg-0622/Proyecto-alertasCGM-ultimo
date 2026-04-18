from flask import Blueprint, render_template, request
from . import db
from app.models.alertas import Alerta
from app.models.servicio import Servicio     
from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import func
from app.auth import login_required
from sqlalchemy import cast, Date



# Define el blueprint una sola vez
bp = Blueprint('alertas', __name__, url_prefix='/alertas')




###################################   Detalle alertas   ####################

###################################   Detalle alertas  - me muestra las cantidad de alertas por clouwash y dynatrace y mas  ####################


@bp.route('/detalle_alertas', methods=['GET', 'POST'])
@login_required
def detalle_alertas():
    # 1. Obtener parámetros (se mantiene igual)
    servicio_param = request.args.get('servicio', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()
    host_param = request.args.get('Host', '').strip()
    operational_data_param = request.args.get('Operational_data', '').strip()
    rango_duracion_param = request.args.get('Rango_Duracion', '').strip()
    problem_param = request.args.get('problem', '').strip()

    # 2. Función para aplicar filtros a cualquier consulta
    def aplicar_filtros(q):
        if fecha_inicio_str:
            try:
                f_ini = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                q = q.filter(Alerta.time >= f_ini)
            except: pass
        if fecha_fin_str:
            try:
                f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)
                q = q.filter(Alerta.time < f_fin)
            except: pass
        
        if servicio_param and servicio_param != 'None':
            q = q.filter(Alerta.servicio == servicio_param)
        if host_param and host_param != 'None':
            q = q.filter(Alerta.host.ilike(f'%{host_param}%'))
        if operational_data_param and operational_data_param != 'None':
            q = q.filter(Alerta.operational_data.ilike(f'%{operational_data_param}%'))
        if rango_duracion_param and rango_duracion_param != 'None':
            q = q.filter(Alerta.rango_duracion == rango_duracion_param)
        if problem_param and problem_param != 'None':
            q = q.filter(Alerta.problem == problem_param)
        return q

    # --- CONSULTA 1: Registros Detallados ---
    query_det = Alerta.query.order_by(Alerta.time.desc())
    alertas_raw = aplicar_filtros(query_det).all()
    
    # Formateamos manualmente para la plantilla (reemplaza lo que hacía Pandas)
    alertas_list = []
    for a in alertas_raw:
        alertas_list.append({
            'id': a.id,
            'Servicio': a.servicio,
            'Host': a.host,
            'Time': a.time,
            'Fecha_Hora': a.time.strftime('%d/%m/%Y %H:%M') if a.time else '',
            'Operational_data': a.operational_data,
            'Rango_Duracion': a.rango_duracion,
            'Problem': a.problem,
            'Severity': a.severity
        })

    # --- CONSULTA 2: Gráfico (Conteo por día) ---
    query_grafico = db.session.query(
        cast(Alerta.time, Date).label('Fecha'),
        func.count(Alerta.id).label('Cantidad_Alertas')
    ).group_by(cast(Alerta.time, Date)).order_by('Fecha')
    
    grafico_data = [r._asdict() for r in aplicar_filtros(query_grafico).all()]

    # --- CONSULTA 3: Conteos de Categorías (Hosts, Rangos, Problemas) ---
    def obtener_conteo(columna):
        q = db.session.query(columna, func.count(Alerta.id)).group_by(columna)
        return dict(aplicar_filtros(q).all())

    conteo_hosts = obtener_conteo(Alerta.host)
    conteo_rango_duracion = obtener_conteo(Alerta.rango_duracion)
    conteo_problem = obtener_conteo(Alerta.problem)

    return render_template(
        'alertas/detalle_alertas.html',
        alertas=alertas_list,
        grafico_data=grafico_data,
        Host=host_param,
        conteo_hosts=conteo_hosts,
        conteo_rango_duracion=conteo_rango_duracion,
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str,
        servicios={'Servicio': servicio_param},
        problem={'Problem': problem_param}
    )



###################################   top 20  ####################

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









#################3#################################   Alertas con entregado_cgm = no   ####################



from collections import Counter


@bp.route('/alertas_tag_entregado_cgm_no', methods=['GET', 'POST'])
@login_required
def alertas_tag_entregado_cgm_no():
    # 1. Obtener parámetros
    servicio_seleccionado = request.args.get('servicio', '').strip()
    host_filtro = request.args.get('host', '').strip() # Cambiado a minúscula para consistencia
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()

    # --- CONSULTA PARA EL SELECT ---
    servicios_unicos = db.session.query(Alerta.servicio).filter(
        Alerta.entregado_cgm.ilike('no')
    ).distinct().order_by(Alerta.servicio).all()

    lista_servicios = [s[0] for s in servicios_unicos if s[0]]
    print(f"DEBUG: Servicios únicos con entregado_cgm='no': {lista_servicios}")

    def aplicar_filtros(q):
        q = q.filter(Alerta.entregado_cgm.ilike('no'))
        if servicio_seleccionado:
            q = q.filter(Alerta.servicio == servicio_seleccionado)
        if host_filtro:
            q = q.filter(Alerta.host.ilike(f'%{host_filtro}%'))
        
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

    # CONSULTA 1: Datos detallados
    query_datos = db.session.query(
        Alerta.id, Alerta.time, Alerta.servicio, Alerta.problem,
        Alerta.entregado_cgm, Alerta.operational_data, Alerta.rango_duracion, Alerta.host
    )
    query_datos = aplicar_filtros(query_datos)
    alertas_list = [r._asdict() for r in query_datos.all()]

    # --- GENERAR CONTEO DE HOSTS DESDE LA LISTA ---
    conteo_hosts = Counter(alerta.get('host') or 'DESCONOCIDO' for alerta in alertas_list)

    # CONSULTA 2: Conteo agrupado por servicio
    query_conteo = db.session.query(
        Alerta.servicio.label('Servicio'), 
        func.count(Alerta.id).label('Total_Alertas')
    ).group_by(Alerta.servicio).order_by(func.count(Alerta.id).desc())
    query_conteo = aplicar_filtros(query_conteo)
    conteo_servicios = [r._asdict() for r in query_conteo.all()]

    return render_template(
        'alertas/tag_entregado_cgm_no.html', 
        alertas=alertas_list,
        conteo_servicios=conteo_servicios,
        conteo_hosts=conteo_hosts,
        servicios_dropdown=lista_servicios,
        fecha_inicio=fecha_inicio_str, 
        fecha_fin=fecha_fin_str,
        servicio_seleccionado=servicio_seleccionado,
        host_seleccionado=host_filtro
    )



###########################entregado_cgm_por_servico_iguales ######################



@bp.route('/entregado_cgm_por_servico_iguales', methods=['GET'])
@login_required
def entregado_cgm_por_servico_iguales():
    # Consulta: Agrupar por servicio y contar IDs donde entregado_cgm es 'no'
    resumen_query = db.session.query(
        Alerta.servicio.label('servicio'),
        func.count(Alerta.id).label('total')).filter(
Alerta.entregado_cgm.ilike('no')
    ).group_by(
        Alerta.servicio
    ).order_by(
        func.count(Alerta.id).desc()
    ).all()

    # Convertir a lista de diccionarios para el template
    resumen_list = [r._asdict() for r in resumen_query]
    
    # Calcular gran total
    total_general = sum(item['total'] for item in resumen_list)

    return render_template(
        'alertas/entregado_cgm_por_servico_iguales.html',
        resumen=resumen_list,
        total_general=total_general
    )



################################## Conteo por servicio con tags entregado_cgm = no y descripcion igual   ####################
@bp.route('/conteo_servicio_tags', methods=['GET'])
@login_required
def conteo_servicio_tags():
    # 1. Parámetros
    fecha_inicio = request.args.get('fecha_inicio', '').strip()
    fecha_fin = request.args.get('fecha_fin', '').strip()
    servicio_filtro = request.args.get('servicio_filtro', '').strip()

    # 2. Consulta para la TABLA (Ya tiene el filtro 'no')
    query = db.session.query(
        Alerta.servicio.label('servicio'),
        Alerta.operational_data.label('operational_data'),
        func.count(Alerta.id).label('total')
    ).filter(
        Alerta.entregado_cgm.ilike('no'),
        Alerta.operational_data.isnot(None),
        Alerta.operational_data != ''
    )

    # Filtros dinámicos para la tabla
    if servicio_filtro:
        query = query.filter(Alerta.servicio == servicio_filtro)
    if fecha_inicio and fecha_fin:
        query = query.filter(Alerta.time.between(fecha_inicio, fecha_fin))

    resumen_query = query.group_by(
        Alerta.servicio, 
        Alerta.operational_data
    ).order_by(func.count(Alerta.id).desc()).all()

    # 3. CORRECCIÓN: Consulta para el DROPDOWN (Solo servicios con 'no')
    servicios_raw = db.session.query(Alerta.servicio)\
        .filter(Alerta.entregado_cgm.ilike('no'))\
        .distinct()\
        .all()
    
    # Limpiar lista de tuplas
    lista_servicios = sorted([s[0] for s in servicios_raw if s[0]])

    resumen_list = [r._asdict() for r in resumen_query]
    total_general = sum(item['total'] for item in resumen_list)

    return render_template(
        'alertas/conteo_servicio+tags_iguales.html',
        resumen=resumen_list,
        total_general=total_general,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        servicio_filtro=servicio_filtro,
        servicios_dropdown=lista_servicios
    )


################### alertas menores a 5 minutos por servicio ####################

from sqlalchemy import func
from datetime import datetime, timedelta

@bp.route('/alertas_menores_5min', methods=['GET', 'POST'])
@login_required
def alertas_menores_5min():
    servicio = request.args.get('servicio', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()

    # 1. Base de la consulta: Agrupamos por servicio y contamos
    query_conteo = db.session.query(
        Alerta.servicio.label('Servicio'),
        func.count(Alerta.id).label('Total_Alertas')
    ).group_by(Alerta.servicio)

    # 2. FILTRO CLAVE: Filtrar solo las filas que tengan el rango "<5 min"
    # Este es un filtro de fila (WHERE), no de grupo (HAVING)
    query_conteo = query_conteo.filter(Alerta.rango_duracion == '<5 min')

    # 3. Filtros adicionales (Servicio y Fechas)
    if servicio:
        query_conteo = query_conteo.filter(Alerta.servicio.ilike(f'%{servicio}%'))
    
    if fecha_inicio_str:
        try:
            f_ini = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            query_conteo = query_conteo.filter(Alerta.time >= f_ini)
        except: pass
        
    if fecha_fin_str:
        try:
            # Aquí filtramos por Alerta.time, no por rango_duracion
            f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)
            query_conteo = query_conteo.filter(Alerta.time < f_fin)
        except: pass

    # 4. Ordenar por los servicios que más alertas de este tipo tienen
    query_conteo = query_conteo.order_by(func.count(Alerta.id).desc())
    
    conteo_servicios = [r._asdict() for r in query_conteo.all()]
    total_general_rapidas = sum(item['Total_Alertas'] for item in conteo_servicios)

    return render_template(
        'alertas/alertas_menores_5minutos.html',
        conteo_servicios=conteo_servicios,
        total_general=total_general_rapidas, # Enviamos el gran total
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str
    )


######################################## detalle menores a 5 minutos por servicio ####################



from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta

@bp.route('/detalle_alertas_menores_5min', methods=['GET', 'POST']) # Le damos un nombre único
@login_required
def detalle_alertas_menores_5min():
    # 1. Obtener parámetros
    servicio_param = request.args.get('servicio', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()
    host_param = request.args.get('Host', '').strip()
    operational_data_param = request.args.get('Operational_data', '').strip()
    problem_param = request.args.get('problem', '').strip()

    # 2. Función de filtrado optimizada
    def aplicar_filtros(q):
        # FILTRO OBLIGATORIO: Solo alertas de menos de 5 min
        q = q.filter(Alerta.rango_duracion == '<5 min')

        if fecha_inicio_str:
            try:
                f_ini = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                q = q.filter(Alerta.time >= f_ini)
            except: pass
        if fecha_fin_str:
            try:
                f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)
                q = q.filter(Alerta.time < f_fin)
            except: pass
        
        if servicio_param and servicio_param != 'None':
            q = q.filter(Alerta.servicio == servicio_param)
        if host_param and host_param != 'None':
            q = q.filter(Alerta.host.ilike(f'%{host_param}%'))
        if operational_data_param and operational_data_param != 'None':
            q = q.filter(Alerta.operational_data.ilike(f'%{operational_data_param}%'))
        if problem_param and problem_param != 'None':
            q = q.filter(Alerta.problem == problem_param)
        return q

    # --- CONSULTA 1: Listado de Alertas Detallado ---
    query_det = Alerta.query.order_by(Alerta.time.desc())
    alertas_raw = aplicar_filtros(query_det).all()
    
    alertas_list = []
    for a in alertas_raw:
        alertas_list.append({
            'id': a.id,
            'Servicio': a.servicio,
            'Host': a.host,
            'Time': a.time,
            'Fecha_Hora': a.time.strftime('%d/%m/%Y %H:%M') if a.time else '',
            'Operational_data': a.operational_data,
            'Rango_Duracion': a.rango_duracion,
            'Problem': a.problem,
            'Severity': a.severity
        })

    # --- CONSULTA 2: Data para el Gráfico (solo de <5 min) ---
    query_grafico = db.session.query(
        cast(Alerta.time, Date).label('Fecha'),
        func.count(Alerta.id).label('Cantidad_Alertas')
    ).group_by(cast(Alerta.time, Date)).order_by('Fecha')
    
    grafico_data = [r._asdict() for r in aplicar_filtros(query_grafico).all()]

    # --- CONSULTA 3: Conteos laterales ---
    def obtener_conteo(columna):
        q = db.session.query(columna, func.count(Alerta.id)).group_by(columna)
        # Aplicamos el filtro para que el conteo sea solo de las rápidas
        return dict(aplicar_filtros(q).all())

    conteo_hosts = obtener_conteo(Alerta.host)
    conteo_problem = obtener_conteo(Alerta.problem)

    return render_template(
        'alertas/detalle_alertas_menor5min.html', # Reusamos tu plantilla de detalle
        alertas=alertas_list,
        grafico_data=grafico_data,
        Host=host_param,
        conteo_hosts=conteo_hosts,
        conteo_rango_duracion={'<5 min': len(alertas_list)}, # Valor fijo ya que filtramos por esto
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str,
        servicios={'Servicio': servicio_param},
        problem={'Problem': problem_param}
    )

  

  ############################# conteo de alertas iguales menores a 5 minutos por servicio ####################
@bp.route('/conteo_alertas_iguales_menores_5_min', methods=['GET'])
@login_required
def conteo_alertas_iguales_menores_5_min():
    servicio_param = request.args.get('servicio', '').strip()
    fecha_inicio_str = request.args.get('fecha_inicio', '').strip()
    fecha_fin_str = request.args.get('fecha_fin', '').strip()

    # 1. Total histórico global (Solo alertas < 5 min sin ningún otro filtro)
    total_historico = db.session.query(func.count(Alerta.id))\
        .filter(Alerta.rango_duracion == '<5 min').scalar() or 0

    # 2. Servicios para el dropdown
    servicios_disponibles = [
        s[0] for s in db.session.query(Alerta.servicio)
        .filter(Alerta.rango_duracion == '<5 min')
        .distinct().order_by(Alerta.servicio).all()
    ]

    # 3. Consulta de conteo agrupado
    query_conteo = db.session.query(
        Alerta.servicio,
        Alerta.operational_data,
        func.count(Alerta.id).label('cantidad')
    ).group_by(Alerta.servicio, Alerta.operational_data)

    # Filtro obligatorio
    query_conteo = query_conteo.filter(Alerta.rango_duracion == '<5 min')

    # 4. Aplicar filtros dinámicos
    if fecha_inicio_str:
        try:
            f_ini = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            query_conteo = query_conteo.filter(Alerta.time >= f_ini)
        except: pass
    if fecha_fin_str:
        try:
            f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)
            query_conteo = query_conteo.filter(Alerta.time < f_fin)
        except: pass
    if servicio_param and servicio_param != 'None':
        query_conteo = query_conteo.filter(Alerta.servicio == servicio_param)

    # 5. Resultados
    conteo_resultado = query_conteo.order_by(func.count(Alerta.id).desc()).all()
    
    # Calcular total de alertas BAJO EL FILTRO ACTUAL
    total_filtrado = sum(r.cantidad for r in conteo_resultado)
    
    conteo = [
        {'servicio': r.servicio, 'operational_data': r.operational_data, 'cantidad': r.cantidad}
        for r in conteo_resultado
    ]

    return render_template(
        'alertas/conteo_alertas_iguales_menores_5_min.html', 
        conteo_por_servicio_y_alerta=conteo, 
        servicios_disponibles=servicios_disponibles,
        total_historico=total_historico,
        total_filtrado=total_filtrado,
        fecha_inicio=fecha_inicio_str,
        fecha_fin=fecha_fin_str
    )
