from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
import app


class RegistracijosForma(FlaskForm):
    vardas = StringField('Vardas', [DataRequired()])
    el_pastas = StringField('El. paštas', [DataRequired()])
    slaptazodis = PasswordField('Slaptažodis', [DataRequired()])
    patvirtintas_slaptazodis = PasswordField("Pakartokite slaptažodį", [EqualTo('slaptazodis', "Slaptažodis turi sutapti.")])
    submit = SubmitField('Prisiregistruoti')


class PrisijungimoForma(FlaskForm):
    el_pastas = StringField('El. paštas', [DataRequired()])
    slaptazodis = PasswordField('Slaptažodis', [DataRequired()])
    prisiminti = BooleanField("Prisiminti mane")
    submit = SubmitField('Prisijungti')

def get_pk(obj):
    return str(obj)

def saskaita_query():
    return app.Saskaita.query

def group_query():
    return app.Group.query

class GroupForm(FlaskForm):
    pavadinimas = StringField('Pavadinimas', [DataRequired()])
    #pavarde = StringField('Pavardė', [DataRequired()])
    saskaitos = QuerySelectMultipleField(query_factory=saskaita_query, get_label="apibudinimas", get_pk=get_pk)
    submit = SubmitField('Įvesti')

class SaskaitaForm(FlaskForm):
    apibudinimas = StringField('Apibūdinimas(sąskaita priskiriama sąskaitų grupei)', [DataRequired()])
    #pastabos = StringField('Pastabos', [DataRequired()])
    suma  = IntegerField('Suma', [DataRequired()])
    group = QuerySelectField(query_factory=group_query, get_label="pavadinimas", get_pk=get_pk)
    submit = SubmitField('Įvesti')
