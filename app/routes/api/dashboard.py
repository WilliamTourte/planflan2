"""API Dashboard - Endpoints pour les données du tableau de bord."""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Flan, Evaluation, Etablissement
from app.extensions import db

# Créer un blueprint pour les endpoints API du dashboard
dashboard_api_bp = Blueprint("dashboard_api", __name__, url_prefix="/api/dashboard")


@dashboard_api_bp.route("/user/flans", methods=["GET"])
@login_required
def get_user_flans():
    """Retourne les flans proposés par l'utilisateur courant.

    Returns:
        JSON: Liste des flans avec pagination
    """
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = Flan.query.filter_by(id_user=current_user.id_user).order_by(Flan.id_flan.desc())

    total = query.count()
    flans = query.offset(offset).limit(limit).all()

    return jsonify(
        {
            "data": [flan.to_dict(include_etablissement=True) for flan in flans],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@dashboard_api_bp.route("/user/evaluations", methods=["GET"])
@login_required
def get_user_evaluations():
    """Retourne les évaluations de l'utilisateur courant.

    Returns:
        JSON: Liste des évaluations avec pagination
    """
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = Evaluation.query.filter_by(id_user=current_user.id_user).order_by(
        Evaluation.date_creation.desc()
    )

    total = query.count()
    evaluations = query.offset(offset).limit(limit).all()

    return jsonify(
        {
            "data": [eval.to_dict(include_flan=True) for eval in evaluations],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@dashboard_api_bp.route("/admin/recent_etablissements", methods=["GET"])
@login_required
def get_recent_etablissements():
    """Retourne les derniers établissements ajoutés (admin seulement).

    Returns:
        JSON: Liste des établissements avec pagination
    """
    if not current_user.is_admin:
        return jsonify({"error": "Accès refusé"}), 403

    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = Etablissement.query.order_by(Etablissement.id_etab.desc())

    total = query.count()
    etablissements = query.offset(offset).limit(limit).all()

    return jsonify(
        {
            "data": [etab.to_dict(include_flans=False) for etab in etablissements],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@dashboard_api_bp.route("/admin/recent_flans", methods=["GET"])
@login_required
def get_recent_flans():
    """Retourne les derniers flans ajoutés (admin seulement).

    Returns:
        JSON: Liste des flans avec pagination
    """
    if not current_user.is_admin:
        return jsonify({"error": "Accès refusé"}), 403

    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = Flan.query.order_by(Flan.id_flan.desc())

    total = query.count()
    flans = query.offset(offset).limit(limit).all()

    return jsonify(
        {
            "data": [flan.to_dict(include_etablissement=True) for flan in flans],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@dashboard_api_bp.route("/admin/recent_evaluations", methods=["GET"])
@login_required
def get_recent_evaluations():
    """Retourne les dernières évaluations ajoutées (admin seulement).

    Returns:
        JSON: Liste des évaluations avec pagination
    """
    if not current_user.is_admin:
        return jsonify({"error": "Accès refusé"}), 403

    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = Evaluation.query.order_by(Evaluation.date_creation.desc())

    total = query.count()
    evaluations = query.offset(offset).limit(limit).all()

    return jsonify(
        {
            "data": [
                eval.to_dict(include_flan=True, include_utilisateur=True) for eval in evaluations
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )
