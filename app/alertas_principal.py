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

    # Obtener el valor del filtro desde el query string
    label = request.args.get('label', '').strip()

    # Filtrar servicios si se ingresó un valor
    if label:
        servicios_info = (
            db.session.query(Servicio)
            .filter(Servicio.servicio.ilike(f'%{label}%'))
            .all()
        )
    else:
        servicios_info = db.session.query(
            Servicio.servicio,
            Servicio.encargado_cgm,
            Servicio.servicio_especial,
            Servicio.servicio_clave
        ).all()

    print(f"Servicios encontrados: {len(servicios_info)}")

    # Top 20 servicios con más alertas
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
        servicios_info=servicios_info
    )



