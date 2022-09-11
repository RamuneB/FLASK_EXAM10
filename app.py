from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import forms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slaptas_raktas'
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
db = SQLAlchemy(app)


# Reikia instaliuoti:
# pip install flask-login
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
login_manager = LoginManager()
login_manager.init_app(app)


# Reikia instaliuoti:
# pip install flask-bcrypt
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


class Vartotojas(db.Model, UserMixin):
    __tablename__ = "vartotojas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String(20), unique=True, nullable=False)
    el_pastas = db.Column("El. pašto adresas", db.String(120), unique=True, nullable=False)
    slaptazodis = db.Column("Slaptažodis", db.String(60), unique=True, nullable=False)

class Group(db.Model):
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key=True)
    pavadinimas = db.Column("Pavadinimas", db.String)
    #pavarde = db.Column("Pavardė", db.String)
    saskaitos = db.relationship("Saskaita")


class Saskaita(db.Model):
    __tablename__ = "saskaita"
    id = db.Column(db.Integer, primary_key=True)
    apibudinimas = db.Column("Apibūdinimas", db.String)
    suma = db.Column(db.Integer, nullable=False)
    #pastabos = db.Column("Pastabos", db.String)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group")



@login_manager.user_loader
def load_user(user_id):
    return Vartotojas.query.get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registracija', methods=['GET', 'POST'])
def register():
    form = forms.RegistracijosForma()
    if form.validate_on_submit():
        koduotas_slaptazodis = bcrypt.generate_password_hash(form.slaptazodis.data).decode('utf-8')
        vartotojas = Vartotojas(vardas=form.vardas.data, el_pastas=form.el_pastas.data, slaptazodis=koduotas_slaptazodis)
        db.session.add(vartotojas)
        db.session.commit()
        # flash('Sėkmingai prisiregistravote! Galite prisijungti', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/prisijungti', methods=['GET', 'POST'])
def login():
    form = forms.PrisijungimoForma()
    if form.validate_on_submit():
        user = Vartotojas.query.filter_by(el_pastas=form.el_pastas.data).first()
        if user and bcrypt.check_password_hash(user.slaptazodis, form.slaptazodis.data):
            login_user(user, remember=form.prisiminti.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('parents'))
        # else:
            # flash('Prisijungti nepavyko. Patikrinkite el. paštą ir slaptažodį', 'danger')
    return render_template('login.html', form=form)


@app.route("/atsijungti")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/profilis")
@login_required
def profile():
    return render_template('profilis.html', title='Įrašai')




@app.route("/groups")
def parents():
    try:
        visi_groups = Group.query.all()
    except:
        visi_groups = []
    return render_template("groups.html", visi_groups=visi_groups)


@app.route("/saskaitos")
def children():
    try:
        visi_saskaitos = Saskaita.query.all()
    except:
        visi_saskaitos = []
    return render_template("bills.html", visi_saskaitos=visi_saskaitos)


@app.route("/naujas_group", methods=["GET", "POST"])
def new_parent():
    db.create_all()
    forma = forms.GroupForm()
    if forma.validate_on_submit():
        naujas_group = Group(pavadinimas=forma.pavadinimas.data)
        for saskaita in forma.saskaitos.data:
            priskirtas_saskaita = Saskaita.query.get(saskaita.id)
            naujas_group.saskaitos.append(priskirtas_saskaita)
        db.session.add(naujas_group)
        db.session.commit()
        return redirect(url_for('parents'))
    return render_template("prideti_group.html", form=forma)

@app.route("/istrinti_group/<int:id>")
def istrinti_grupe(id):
    uzklausa = Group.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for('parents'))

@app.route("/redaguoti_group/<int:id>", methods=['GET', 'POST'])
def redaguoti_grupe(id):
    forma = forms.GroupForm()
    group = Group.query.get(id)
    if forma.validate_on_submit():
        #grupe.vardas = forma.vardas.data
        group.pavadinimas = forma.pavadinimas.data
       
        group.saskaitos = []
        for saskaita in forma.saskaitos.data:
            priskirta_saskaita = Saskaita.query.get(saskaita.id)
            group.saskaitos.append(priskirta_saskaita)
        db.session.commit()
        return redirect(url_for('parents'))
    return render_template("redaguoti_group.html", form=forma, group=group)

@app.route("/istrinti_saskaita/<int:id>")
def istrinti_saskaita(id):
    uzklausa = Saskaita.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for('children'))

@app.route("/naujas_saskaita", methods=["GET", "POST"])
def new_child():
    db.create_all()
    forma = forms.SaskaitaForm()
    if forma.validate_on_submit():
        naujas_saskaita = Saskaita(apibudinimas=forma.apibudinimas.data,
                                suma=forma.suma.data)
                                
        db.session.add(naujas_saskaita)
        db.session.commit()
        return redirect(url_for('children'))
    return render_template("prideti_bill.html", form=forma)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
