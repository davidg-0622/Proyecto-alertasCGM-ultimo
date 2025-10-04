from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.servicio import Servicio
from app import db # Asume que 'db' se importa desde la aplicación principal
from math import ceil


# Define el blueprint una sola vez
bp = Blueprint('app', __name__, url_prefix='/app')


###########################Listar servicio #####################

@bp.route('/listar')
def listar():
    filtro = request.args.get('filtro')
    page = request.args.get('page', 1, type=int)  # página actual
    per_page = 1  # cantidad de registros por página

    query = Servicio.query

    if filtro:
        query = query.filter(Servicio.servicio.ilike(f'%{filtro}%'))
       

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

@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/create')
def create():
    return "crear servicio "
