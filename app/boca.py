from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from app.models.servicio import Servicio     
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
from app.auth import login_required




# Define el blueprint una sola vez
bp = Blueprint('boca', __name__, url_prefix='/boca')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def notificar_boca():
    servicios_filtrados = []
    
    # Preparamos los datos para la lista de servicios (datalist)
    todos_los_servicios_db = Servicio.query.with_entities(Servicio.servicio, Servicio.codigo_de_aplicacion, Servicio.descripcion_del_servicio, Servicio.promesa_del_servicio, Servicio.sre, ).all()
    print(todos_los_servicios_db)
    nombres_servicios = [s.servicio for s in todos_los_servicios_db]

    input_servicio_valor = ""
    input_estado_valor = ""
    frase_completa_final = None # <-- Nueva variable para la frase final

    if request.method == 'POST':
        input_estado_valor = request.form.get('estado_servicio')
        input_servicio_valor = request.form.get('termino_busqueda', '').strip()

        if input_estado_valor and input_servicio_valor:
            # Aquí es donde construimos la frase en Python
            if input_estado_valor == 'validando':
                frase_base = "🗣️ Nos encontramos validando alertas para el servicio de"
            elif input_estado_valor == 'normalidad':
                frase_base = "✅ Se presenta normalidad para el servicio de"
            elif input_estado_valor == 'descartando':
                frase_base = "✅ Se descarta afectación para el servicio de"
            else:
                frase_base = ""
            
            # Concatenamos la frase base con el nombre del servicio seleccionado
            frase_completa_final = f"{frase_base} {input_servicio_valor}"

            # Lógica de filtrado de la tabla (sin cambios)
            servicios_filtrados = Servicio.query.filter(
                Servicio.servicio == input_servicio_valor
            ).all()
            
            if not servicios_filtrados:
                 flash(f"No se encontró el servicio en la BD.", 'warning')
            
        else:
            flash("Por favor, complete ambos campos (frase y servicio).", 'info')

    # Pasar todas las variables necesarias a la plantilla, incluyendo la nueva frase
    return render_template('bocas/boca.html', 
                           servicios_filtrados=servicios_filtrados, 
                           valor_anterior_servicio=input_servicio_valor,
                           valor_anterior_estado=input_estado_valor,
                           nombres_servicios_lista=nombres_servicios,
                           frase_generada=frase_completa_final) # <-- Nueva variable






############################### Lotes de pago ####################################

# Asegúrate de que tus imports en la parte superior del archivo son correctos:
# from flask import render_template, request, flash, redirect, url_for
# from flask_login import login_required
# from . import bp # Suponiendo que usas un Blueprint

@bp.route('/lotes_de_pago', methods=['GET', 'POST'])
@login_required
def lotes_de_pago():
    frase_completa_final = None
    valores_anteriores = {} 

    if request.method == 'POST':
        tipo_notificacion_value = request.form.get('boca_lotes_pago')
        descripcion_afectacion = request.form.get('descripcion_afectacion', '').strip()
        hora_inicio_retencion = request.form.get('hora_inicio_retencion')
        hora_inicio_dosificacion = request.form.get('hora_inicio_dosificacion')
        lotes_retenidos = request.form.get('lotes_retenidos', '').strip()
        lotes_procesados = request.form.get('lotes_procesados', '').strip()
        lotes_fallidos = request.form.get('lotes_fallidos', '').strip()
        lotes_por_minuto = request.form.get('lotes_por_minuto', '').strip()
        hora_ok_valor = request.form.get('hora_ok', '').strip() # Nuevo campo capturado

        # Guardar valores para repoblar el formulario
        valores_anteriores = {
            'tipo_notificacion': tipo_notificacion_value,
            'descripcion_afectacion': descripcion_afectacion,
            'hora_inicio_retencion': hora_inicio_retencion,
            'hora_inicio_dosificacion': hora_inicio_dosificacion,
            'lotes_retenidos': lotes_retenidos,
            'lotes_procesados': lotes_procesados,
            'lotes_fallidos': lotes_fallidos,
            'lotes_por_minuto': lotes_por_minuto,
            'hora_ok': hora_ok_valor,
        }

        # Mapeo del texto base (asegúrate de que los values coincidan con el HTML)
        tipo_notificacion_text = ""
        if tipo_notificacion_value == 'sve_validando':
            tipo_notificacion_text = "🗣️ Lotes de Pago por la Sucursal Virtual Empresas Bancolombia"
        elif tipo_notificacion_value == 'svn_validando':
            tipo_notificacion_text = "🗣️ Lotes de Pago por la Sucursal Virtual Negocios"
        elif tipo_notificacion_value == 'normalidad':
            tipo_notificacion_text = "✅ Lotes de Pago por la Sucursal Virtual Empresas Bancolombia (Normalidad)"
        elif tipo_notificacion_value == 'descartando':
            tipo_notificacion_text = "✅ Lotes de Pago por la Sucursal Virtual Empresas Bancolombia (Descartando)"
        
        # Inicio de la frase con el primer salto de línea
        frase_completa_final = tipo_notificacion_text + "\n"

        # Construcción del detalle: solo añade líneas si los datos existen
        if descripcion_afectacion:
            frase_completa_final += f"{descripcion_afectacion}\n"
        
        if hora_inicio_retencion:
            frase_completa_final += f"Hora Inicio Retención: {hora_inicio_retencion}\n"

        if hora_inicio_dosificacion:
             frase_completa_final += f"Hora Inicio Dosificación: {hora_inicio_dosificacion}\n"
        
        # Inserta Hora OK si existe
        if hora_ok_valor:
             frase_completa_final += f"Hora OK: {hora_ok_valor}\n"

        if lotes_retenidos:
             frase_completa_final += f"Lotes Retenidos: {lotes_retenidos}\n"
             
        if lotes_procesados:
             frase_completa_final += f"Lotes Procesados: {lotes_procesados}\n"
             
        if lotes_fallidos:
             frase_completa_final += f"Lotes Fallidos: {lotes_fallidos}\n"
             
        if lotes_por_minuto:
             frase_completa_final += f"Dosificación de Lotes por Minuto: {lotes_por_minuto}\n"


    # Renderizar el template
    return render_template(
        'bocas/lotes_de_pago.html',
        frase_generada=frase_completa_final,
        valores_anteriores=valores_anteriores
    )

