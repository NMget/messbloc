from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
	__tablename__="user"
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(20), nullable = False, unique = True)
	password = db.Column(db.String(80), nullable = False)
	admin = db.Column(db.Boolean)
	active = db.Column(db.Boolean)
	demande = db.relationship("Demande", backref='user')

class Demande(db.Model):
	__tablename__="demande"
	id = db.Column(db.Integer, primary_key = True)
	demandeur = db.Column(db.String)
	date_debut = db.Column(db.String)
	date_fin = db.Column(db.String)
	adr_nom = db.Column(db.String)
	sens = db.Column(db.String)
	liste = db.Column(db.String)
	nliste = db.Column(db.String)
	motif = db.Column(db.String)
	etat = db.Column(db.String)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, demandeur, date_debut, date_fin, adr_nom, sens, liste, nliste, motif, etat, user_id):
		self.demandeur = demandeur
		self.date_debut = date_debut
		self.date_fin = date_fin
		self.adr_nom = adr_nom
		self.sens = sens
		self.liste = liste
		self.nliste = nliste
		self.motif = motif
		self.etat = etat
		self.user_id = user_id