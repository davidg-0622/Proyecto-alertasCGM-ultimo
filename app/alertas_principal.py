from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from app.models.alertas import Alerta
from app.models.servicio import Servicio     



# Define el blueprint una sola vez
bp = Blueprint('alertas', __name__, url_prefix='/alertas')


@bp.route('/')
def total_alertas():
    # Total de alertas
    alertas = db.session.query(Alerta).count()

    # Parámetros de búsqueda y paginación
    label = request.args.get('label', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 1  # Número de servicios por página

    # Consulta base
    query = db.session.query(Servicio)

    # Filtro por nombre de servicio
    if label:
        query = query.filter(Servicio.servicio.ilike(f'%{label}%'))

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
        label=label
    )