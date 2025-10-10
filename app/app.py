from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.servicio import Servicio
from app import db # Asume que 'db' se importa desde la aplicación principal
from math import ceil
from sqlalchemy import or_


# Define el blueprint una sola vez
bp = Blueprint('app', __name__, url_prefix='/app')


###########################Listar servicio #####################

@bp.route('/listar')
def listar():
    filtro = request.args.get('filtro')
    page = request.args.get('page', 1, type=int)

    query = Servicio.query

    if filtro:
        query = query.filter(or_(
            Servicio.servicio.ilike(f'%{filtro}%'),
        ))
        per_page = query.count() or 1  # Si hay filtro, per_page es el número de resultados encontrados
    else:
        per_page = 1  # Sin filtro, per_page es 1

    paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
    servicios = paginacion.items
    total = query.count()
    total_pages = ceil(total / per_page)

    return render_template(
        'servicios/listar_servicio.html',
        servicios=servicios,
        page=page,
        total_pages=total_pages,
        filtro=filtro
    )

########################editar#######################

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def edit_servicio(id):
    """Maneja la edición de un servicio existente."""
    servicio = Servicio.query.get_or_404(id)

    if request.method == 'POST':
        try:
            servicio.codigo_de_aplicacion = request.form['codigo_de_aplicacion']
            servicio.servicio = request.form['servicio']
            servicio.descripcion_del_servicio = request.form['descripcion_del_servicio']
            servicio.promesa_del_servicio = request.form['promesa_del_servicio']
            servicio.sre = request.form['sre']
            servicio.evc = request.form['evc']
            servicio.contacto_del_lider = request.form['contacto_del_lider']
            servicio.po = request.form['po']
            servicio.elemento_de_configuracion = request.form['elemento_de_configuracion']
            servicio.grupo_inc_helix = request.form['grupo_inc_helix']
            servicio.runbook = request.form['runbook']
            servicio.carpeta_servicios_entregados = request.form['carpeta_servicios_entregados']
            servicio.relacion_de_servicios = request.form['relacion_de_servicios']
            servicio.nombre_grupo_stand_by = request.form['nombre_grupo_stand_by']
            servicio.lider_tecnico_evc = request.form['lider_tecnico_evc']
            servicio.lider_linea_area_conocimiento = request.form['lider_linea_area_conocimiento']
            servicio.servicio_especial = request.form['servicio_especial']
            servicio.servicio_clave = request.form['servicio_clave']
            servicio.encargado_cgm = request.form['encargado_cgm']
            servicio.plataforma = request.form['plataforma']

            db.session.commit()
            flash('Servicio actualizado correctamente.', 'success')
            return redirect(url_for('app.listar'))
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar los cambios: {e}")
            flash('Hubo un error al guardar los cambios.', 'danger')
            return redirect(url_for('app.listar'))

    return render_template('servicios/edit_servicio.html', servicio=servicio)


####################### delete ####################

@bp.route('/eliminar/<int:id>', methods=['POST'])
def delete_servicio(id):
    """Elimina un servicio de la base de datos."""
    servicio = Servicio.query.get_or_404(id)
    try:
        db.session.delete(servicio)
        db.session.commit()
        flash('El servicio ha sido eliminado correctamente.', 'success')
        return redirect(url_for('app.listar'))
    except Exception:
        db.session.rollback()
        flash('Hubo un error al eliminar el servicio.', 'danger')
        return redirect(url_for('app.listar'))


#####################################

@bp.route('/')
def index():
     return redirect(url_for('app.listar'))



# Mostrar el formulario
@bp.route('/crear_servicio', methods=['GET'])
def mostrar_formulario_servicio():
    return render_template('servicios/create_servicio.html')

# Procesar el formulario
@bp.route('/crear_servicio', methods=['POST'])
def crear_servicio():
    try:
        data = request.form

        nuevo_servicio = Servicio(
            codigo_de_aplicacion=data.get('codigo_de_aplicacion'),
            servicio=data['servicio'],
            descripcion_del_servicio=data['descripcion_del_servicio'],
            promesa_del_servicio=data['promesa_del_servicio'],
            sre=data['sre'],
            evc=data['evc'],
            contacto_del_lider=data.get('contacto_del_lider'),
            po=data['po'],
            elemento_de_configuracion=data.get('elemento_de_configuracion'),
            grupo_inc_helix=data['grupo_inc_helix'],
            runbook=data.get('runbook'),
            carpeta_servicios_entregados=data.get('carpeta_servicios_entregados'),
            relacion_de_servicios=data.get('relacion_de_servicios'),
            nombre_grupo_stand_by=data.get('nombre_grupo_stand_by'),
            lider_tecnico_evc=data['lider_tecnico_evc'],
            lider_linea_area_conocimiento=data['lider_linea_area_conocimiento'],
            servicio_especial=data.get('servicio_especial'),
            servicio_clave=data.get('servicio_clave'),
            encargado_cgm=data.get('encargado_cgm'),
            plataforma=data['plataforma']
        )

        db.session.add(nuevo_servicio)
        db.session.commit()

        return redirect(url_for('app.listar'))  # o redirige a otra vista
    except Exception as e:
        db.session.rollback()
        return f"Error al crear el servicio: {str(e)}", 400
