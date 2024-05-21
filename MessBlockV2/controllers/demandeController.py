from flask import render_template, request, flash, url_for , redirect
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, HiddenField, StringField, DateField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Regexp, ValidationError
from flask_login import current_user, login_required
from datetime import date
from flask_mail import Mail, Message
from models.models import *

mail = Mail()



class addDemandeForm(FlaskForm):
	id_field = HiddenField()
	demandeur = SelectField('Demandeur', 
				choices=[('',''),('moc', 'MOC'), ('soc','SOC')], validate_choice = False)
	date_debut = DateField('Début du blocage', [InputRequired()], default=date.today, id = "debut")
	date_fin = DateField('Fin du blocage', default=date.today, id = "fin")
	bloc_perm = BooleanField('Blocage Permanent', id = 'bloc_perm', false_values=None)
	adr_nom = StringField('Mail(s) / Domaine(s) à bloquer', [InputRequired(),
		Regexp(r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})(;([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+|[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}))*$')])
	sens = SelectField('Sens', [InputRequired()],
		choices = [('',''),('entrant','ENTRANT'),
				 ('sortant','SORTANT'),('entrant/sortant','ENTANT/SORTANT'), ('entrant WhiteList', 'ENTRANT WHITELIST')])
	liste = StringField ('Liste', [InputRequired()], render_kw={"readonly" : True}, id = "liste")
	nliste = IntegerField('Numero Liste', render_kw={"readonly" : True}, id = 'nliste')
	motif = SelectField('Motif', [InputRequired()],
		     choices = [('', ''), ('spam', 'SPAM'),
		  						('attaque', 'ATTAQUE'), ('phishing', 'PHISHING')])
	etat = SelectField('Etat',[InputRequired()],
		    choices=[('',''), ('ec','EC'),('tt', 'TT')], id = 'etat')
	submit = SubmitField('Ajouter/Modifier')

	def validate_date_fin(self, filed):
		if filed.data < self.date_debut.data:
			raise ValidationError(
				"La date de fin ne peut pas être avant la date de début"
			)

	def validate_demandeur(self, filed):
		if filed.data == "":
			raise ValidationError(
				"Le demandeur doit ne doit pas être null"
			)


class deleteDemandeForm(FlaskForm):
	id_field = HiddenField()
	purpose = HiddenField()
	submit = SubmitField('Supprimer')


@login_required
def add():
	form = addDemandeForm()
	if form.validate_on_submit() :
		demandeur = form.demandeur.data
		date_debut = form.date_debut.data
		if form.bloc_perm.data == True:
			date_fin = None
		else:
			date_fin = form.date_fin.data
		adr_nom = form.adr_nom.data
		sens = form.sens.data
		liste = form.liste.data
		nliste = form.nliste.data
		motif = form.motif.data
		etat = form.etat.data
		user_id = current_user.id
		record = Demande(demandeur, date_debut, date_fin, adr_nom, sens, liste, nliste, motif, etat, user_id)
		db.session.add(record)
		db.session.commit()

		return redirect(url_for('demande_bp.liste'))

	else:
		for field, errors in form.errors.items():
			for error in errors:
				flash("Error in {}: {}".format(
					getattr(form, field).label.text,
					error
				), 'error')
	
	return render_template('bone.html', H2 = "Ajouter une demande", Content = "addDemande.html", form = form, Titre = "Ajouter")


@login_required
def liste():
	demandes = Demande.query.order_by(Demande.id)
	return render_template("bone.html", Titre = "Liste", H2 = 'Liste des demandes', Content = 'liste_demande.html', demandes = demandes)

@login_required
def terminer(id):
	demande = Demande.query.filter(Demande.id == id).first()
	demande.etat = "tt"
	db.session.commit()
	msg = Message('Fin de blocage de "'+ str(demande.adr_nom)+'"', sender="noreply@dgfip.finances.gouv.fr")
	if demande.demandeur == "moc":
		msg.recipients = ["esi.bordeaux.ceisac-messagerie@dgfip.finances.gouv.fr"]
	else:
		msg.recipients = ["esi.bordeaux.ceisac-messagerie@dgfip.finances.gouv.fr"]
	msg.body = """Bonjour,
le blocage de l'adresse/domaine """ + str(demande.adr_nom) + """ arrive à son terme.
Ceci est un message automatique merci de ne pas répondre"""
	mail.send(msg)
	return redirect(url_for('demande_bp.liste'))