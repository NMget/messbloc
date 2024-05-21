from flask import Flask, render_template, request
from flask_login import LoginManager, login_required
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit


from models.models import *
from routes.user_bp import *
from routes.demande_bp import *
from controllers.userController import *
from controllers.demandeController import *


app = Flask(__name__)



Bootstrap(app)

bcrypt.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@192.168.12.2:5432/172.17.0.2'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = 'patate'
db.init_app(app)

app.config['MAIL_SERVER']='smtp.oc.dgfip'
app.config['MAIL_PORT']=25
app.config['MAIL_USERNAME']=''
app.config['MAIL_PASSWORD']=''
app.config['MAIL_USE_TLS']= False
app.config['MAIL_USE_SSL']= False
mail.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_bp.login'

app.register_blueprint(user_bp, url_prefix=None)
app.register_blueprint(demande_bp, url_prefix='/demande')


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route("/")
def index():
	return redirect(url_for('user_bp.login'))

@login_required
@app.route("/dashboard")
def dashboard():
	Titre = "Dashboard"
	Content = "dashboard.html"
	return render_template("bone.html", Content = Content, Titre = Titre)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('bone.html', Titre="404 Error - Page Not Found", H2="Page not found (Error 404)", error=e, Content = "error.html"), 404

@app.errorhandler(405)
def form_not_posted(e):
	return render_template('bone.html', Titre="405 Error - Form Not Submitted", H2="The form was not submitted (Error 405)", error=e, Content = "error.html"), 405

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('bone.html', Titre="500 Error - Internal Server Error", H2="Internal server error (500)", error=e, Content = "error.html"), 500



def my_cron_job():
	print('Tâche planifiée exécutée avec succès !')

	with app.app_context():
		msg = Message('Liste des adresses qui n\'ont pas été débloquée', sender="noreply@dgfip.finances.gouv.fr", recipients=["esi.bordeaux.ceisac-messagerie@dgfip.finances.gouv.fr"])
		demandes = Demande.query.filter(Demande.date_fin <= datetime.today().strftime("%Y-%m-%d"), Demande.etat=="ec")
		msg.body = "Bonjour voici la liste des blocage à débloquer :"
		for demande in demandes:
			msg.body+= "- '" + str(demande.id) + "' adresse/domaine '" + str(demande.adr_nom) + "'"
		mail.send(msg)
	print("Email envoyé")



scheduler = BackgroundScheduler()
scheduler.add_job(func=my_cron_job, trigger="cron",  hour="3", minute="0")
scheduler.start()


atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')