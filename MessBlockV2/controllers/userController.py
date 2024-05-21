from flask import render_template, url_for, redirect
from flask_login import login_user, login_required, logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired,Length, ValidationError
from flask_bcrypt import Bcrypt

from models.models import *

bcrypt = Bcrypt()

class RegisterForm(FlaskForm):
	username = StringField(validators=[InputRequired(), Length(min = 4, max = 20)], render_kw={"placeholder": "Nom d'utilisateur"})
	password = PasswordField(validators=[InputRequired(), Length(min = 4, max = 20)], render_kw={"placeholder": "Mot de passe"})
	admin = BooleanField('Admin')
	active = BooleanField('Active')
	submit = SubmitField("Inscription")

	def validate_username(self, username):
		existing_user_username = User.query.filter_by(username=username.data).first()

		if existing_user_username:
			raise ValidationError(
				"Ce nom d'utilisateur est déjà pris, veuillez en choisir un autre."
			)

class PasswordFrom(FlaskForm):
	username = StringField(validators=[InputRequired(), Length(min = 4, max = 20)], render_kw={"placeholder": "Nom d'utilisateur"})
	oldpw = PasswordField(validators=[InputRequired(),Length(min = 4, max = 20)], render_kw={"placeholder":"Ancien mot de passe"})
	newpw = PasswordField(validators=[InputRequired(),Length(min = 4, max = 20)], render_kw={"placeholder":"Nouveau mot de passe"})
	submit = SubmitField("Modifier")

	def validate_activee(self, username):
		e = User.query.filter_by(username=username.data).first().active.data
		print(e)
		if e == False:
			raise ValidationError(
				"Votre compte à été désactivé"
			)

class LoginForm(FlaskForm):
	username = StringField(validators = [InputRequired(), Length( min = 4, max = 20)], render_kw = {"placeholder": "Nom d'utilisateur"})
	password = PasswordField(validators = [InputRequired(), Length( min = 4, max = 20)], render_kw = {"placeholder": "Mot de passe"})
	submit = SubmitField("Connexion")

	def validate_activee(self, username):
		e = User.query.filter_by(username=username.data).first().active.data
		print(e)
		if e == False:
			raise ValidationError(
				"Votre compte à été désactivé"
			)

def login():
	if current_user.is_authenticated:
		return redirect(url_for('demande_bp.liste'))
	else:
		H2 = "Page de Connexion"
		form = LoginForm()
		if form.validate_on_submit():
			user = User.query.filter_by(username=form.username.data).first()
			if user.active == False:
				raise ValidationError(
					"Votre compte à été désactivé"
				)
			if user:
				if bcrypt.check_password_hash(user.password, form.password.data):
					login_user(user)
					return redirect(url_for('demande_bp.liste'))
	return render_template("bone.html", form =form, Titre = "Connexion", Content = "login.html", H2 = H2)

def password():
	H2 = "Changement de mot de passe"
	form = PasswordFrom()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user.active == False:
			raise ValidationError(
				"Votre compte à été désactivé"
			)
		if user:
			if bcrypt.check_password_hash(user.password, form.oldpw.data):
				hashed_password = bcrypt.generate_password_hash(form.newpw.data).decode('utf-8')
				user.password = hashed_password
				db.session.commit()
				return redirect(url_for("user_bp.login"))
	return render_template("bone.html", H2=H2, form = form, Content = "password.html")


@login_required
def logout():
	logout_user()
	return redirect(url_for('user_bp.login'))




@login_required
def register():
	if current_user.admin == True:
		form = RegisterForm()
		Content = "register.html"
		H2 = "Nouveau compte"
		if form.validate_on_submit():
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			new_user = User(username = form.username.data, password = hashed_password, admin = form.admin.data, active = form.active.data)
			db.session.add(new_user)
			db.session.commit()


	else:
		form = None
		Content = "unautorize.html"
		H2 = "Pas autorisé"

	return render_template("bone.html", form = form, Content = Content, H2 = H2, Titre = "Nouvel Agent")

@login_required
def liste():
	Titre = "Liste Agent"
	if current_user.admin == True:
		users = User.query.all()
		H2 = "Liste des agents"
		Content = "liste_user.html"
	else:
		H2 = 'Pas autorisé'
		Content = "unautorize.html"
		users = None
	return render_template("bone.html", H2 = H2, Content = Content, users = users, Titre = Titre)

@login_required
def admin(id):
	if current_user.admin == True:
		agent = User.query.filter(User.id == id).first()

		agent.admin = not agent.admin
		db.session.commit()

		x = "liste"
	else:
		x = "register"
	return redirect(url_for('user_bp.'+ x))

@login_required
def active(id):
	if current_user.admin == True:
		agent = User.query.filter(User.id == id).first()

		agent.active = not agent.active
		db.session.commit()

		x = "liste"
	else:
		x = "register"
	return redirect(url_for('user_bp.'+ x))