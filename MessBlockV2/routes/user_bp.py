from flask import Blueprint

from controllers.userController import login, logout, register, liste, admin, active, password

user_bp = Blueprint('user_bp',__name__)

user_bp.route('/login', methods=['GET', 'POST'])(login)
user_bp.route('/logout', methods=['GET', 'POST'])(logout)
user_bp.route('/register', methods=['GET','POST'])(register)
user_bp.route('/liste', methods=['GET','POST'])(liste)
user_bp.route('/admin/<id>', methods=['GET', 'POST'])(admin)
user_bp.route('/active/<id>', methods=['GET', 'POST'])(active)
user_bp.route('/password', methods=['GET','POST'])(password)