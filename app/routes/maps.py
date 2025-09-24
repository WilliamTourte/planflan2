from flask import Blueprint, render_template, redirect, url_for


maps_bp = Blueprint('maps', __name__)

@maps_bp.route('/maps')
def maps():
    return render_template('indexmap.html')