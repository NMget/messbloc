from flask import Blueprint

from controllers.demandeController import add, liste, terminer

demande_bp = Blueprint('demande_bp',__name__)

demande_bp.route('/add', methods=['GET', 'POST'])(add)
demande_bp.route('/liste', methods=['GET','POST'])(liste)
demande_bp.route('/terminer/<id>', methods=['GET', 'POST'])(terminer)