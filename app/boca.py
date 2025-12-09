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

@bp.route('/lotes_de_pago', methods=['GET', 'POST'])
@login_required
def lotes_de_pago():
    input_seleccion_afectacion = ""
    input_estado_valor = ""
    frase_completa_final = None # <-- Nueva variable para la frase final

    if request.method == 'POST':
        input_estado_valor = request.form.get('estado_servicio')
        input_servicio_valor = request.form.get('termino_busqueda', '').strip()

        if input_estado_valor and input_servicio_valor:
            # Aquí es donde construimos la frase en Python
            if input_estado_valor == 'boca_sve':
                frase_base = "🗣️ Lotes de Pago por la Sucursal Virtual Empresas Bancolombia"
            elif input_estado_valor == 'boca_svn':
                frase_base = "🗣️ Lotes de Pago por la Sucursal Virtual Negocios"
            elif input_estado_valor == 'normalidad_lotes_svn':
                frase_base = "✅ Lotes de Pago por la Sucursal Virtual Empresas Bancolombia"
            elif input_estado_valor == 'normalidad_lotes_sve':
                frase_base = "✅ Lotes de Pago por la Sucursal Virtual Empresas Bancolombia"
            else:
                frase_base = ""
    return render_template('bocas/lotes_de_pago.html', ) 
