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
    # ... (imports y otras variables) ...
    servicios_filtrados = []
    servicio_para_card = None 

    # 1. Obtenemos todos para el datalist (esto está bien)
    todos_los_servicios_db = Servicio.query.with_entities(Servicio.servicio, Servicio.codigo_de_aplicacion, Servicio.descripcion_del_servicio, Servicio.promesa_del_servicio, Servicio.sre,Servicio.entregado_cgm ).all()
    nombres_servicios = [s.servicio for s in todos_los_servicios_db]
  

 # 2. Inicializamos variables
    input_servicio_valor = ""
    input_estado_valor = ""
    input_transaccion_valor = "" 
    frase_completa_final = None 

    if request.method == 'POST':
        input_estado_valor = request.form.get('estado_servicio')
        input_servicio_valor = request.form.get('termino_busqueda', '').strip()
        input_transaccion_valor = request.form.get('transaccion', '').strip() 

        if input_estado_valor and input_servicio_valor:
            # ... (Lógica de la frase base) ...
            if input_estado_valor == 'validando':
                frase_base = "🗣️ Nos encontramos validando alertas para el servicio de"
            elif input_estado_valor == 'normalidad':
                frase_base = "✅ Se presenta normalidad para el servicio de"
            elif input_estado_valor == 'descartando':
                frase_base = "✅ Se descarta afectación para el servicio de"
            else:
                frase_base = ""
            
            # Usa 'input_transaccion_valor' (con 'n')
            frase_completa_final = f"{frase_base} {input_servicio_valor} {input_transaccion_valor}"

           

            # ... (Resto de la lógica de filtrado) ...
            servicios_filtrados = Servicio.query.filter(Servicio.servicio == input_servicio_valor).all()

            if servicios_filtrados:
                servicio_para_card = servicios_filtrados[0] 
            
            if not servicios_filtrados:
                 flash(f"No se encontró el servicio en la BD.", 'warning')
            
        else:
            flash("Por favor, complete ambos campos (frase y servicio).", 'info')

    # Pasamos la variable correctamente actualizada al render_template
    return render_template('bocas/boca.html', 
                           servicios_filtrados=servicios_filtrados, 
                           valor_anterior_servicio=input_servicio_valor,
                           valor_anterior_estado=input_estado_valor,
                           servicio=servicio_para_card,
                           # Esta variable ahora tiene el valor correcto del POST
                           valor_anterior_transaccion=input_transaccion_valor, 
                           nombres_servicios_lista=nombres_servicios,
                           frase_generada=frase_completa_final)





############################### Lotes de pago ####################################
############################### Lotes de pago ####################################
############################### Lotes de pago ####################################

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
        
        # Convertir a formato 12 horas (no militar)
        hora_inicio_retencion_display = hora_inicio_retencion
        hora_inicio_dosificacion_display = hora_inicio_dosificacion
        
        if hora_inicio_retencion:
            hora_inicio_retencion_display = datetime.strptime(hora_inicio_retencion, '%H:%M').strftime('%I:%M %p')
        if hora_inicio_dosificacion:
            hora_inicio_dosificacion_display = datetime.strptime(hora_inicio_dosificacion, '%H:%M').strftime('%I:%M %p')
        
        lotes_retenidos = request.form.get('lotes_retenidos', '').strip()
        lotes_procesados = request.form.get('lotes_procesados', '').strip()
        lotes_fallidos = request.form.get('lotes_fallidos', '').strip()
        lotes_por_minuto = request.form.get('lotes_por_minuto', '').strip()
        hora_ok_valor = request.form.get('hora_ok', '').strip()
        hora_ok_display = hora_ok_valor
        if hora_ok_valor:
            hora_ok_display = datetime.strptime(hora_ok_valor, '%H:%M').strftime('%I:%M %p')

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
            tipo_notificacion_text = "✅ Lotes de Pago por la Sucursal Virtual Empresas Bancolombia"
        elif tipo_notificacion_value == 'descartando':
            tipo_notificacion_text = "✅ Lotes de Pago por la Sucursal Virtual Negocios "
        
        # Inicio de la frase con el primer salto de línea
        frase_completa_final = tipo_notificacion_text + "\n"

        # Construcción del detalle: solo añade líneas si los datos existen
        if descripcion_afectacion:
            frase_completa_final += f"{descripcion_afectacion}\n"
        
        if hora_inicio_retencion:
            frase_completa_final += f"Hora Inicio Retención: {hora_inicio_retencion_display}\n"

        if hora_inicio_dosificacion:
            frase_completa_final += f"Hora Inicio Dosificación: {hora_inicio_dosificacion_display}\n"
        
        # Inserta Hora OK si existe
        if hora_ok_valor:
            frase_completa_final += f"Hora OK: {hora_ok_display}\n"

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
