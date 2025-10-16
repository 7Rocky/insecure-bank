from threading import Thread

from flask import abort, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

import bot

from app import db
from forms import EditProfileForm, LoginForm, RegisterForm, TransferForm
from models import Transaction, User
from run import app


CSP = "default-src 'self'; style-src 'self'; script-src 'self' https://cdn.jsdelivr.net; img-src 'self'; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; "


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if (form := RegisterForm()).validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Usuario ya registrado')
        else:
            u = User(username=form.username.data, balance=100, bio='¡Hola, acabo de crearme una cuenta!')
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            flash(f'Has recibido {u.balance} € por crear tu cuenta. Puedes iniciar sesión')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (form := LoginForm()).validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()

        if u and u.check_password(form.password.data):
            login_user(u)
            flash('Sesión iniciada')
            return redirect(url_for('profile'))

        flash('Usuario o contraseña incorrectos')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada')
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if (username := request.args.get('username')):
        response = make_response(render_template('profile.html', user=User.query.filter_by(username=username).first()))
        response.headers['Content-Security-Policy'] = CSP
        return response

    if (form := EditProfileForm(obj=current_user)).validate_on_submit():
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Perfil actualizado correctamente.')
        return redirect(url_for('profile'))

    transactions = Transaction.query.filter((Transaction.to_id == current_user.id) | (Transaction.from_id == current_user.id)).order_by(Transaction.timestamp.desc()).all()
    return make_response(render_template('profile.html', form=form, user=current_user, transactions=transactions))


@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if (form := TransferForm()).validate_on_submit():
        if not (to := User.query.filter_by(username=form.to_username.data).first()):
            flash('Usuario receptor no encontrado')
        elif to.id == current_user.id:
            flash('No puedes transferirte a ti mismo')
        elif to.is_admin:
            flash('No puedes transferir dinero al usuario administrador')  # El administrador controla el dinero...
        elif (amt := form.amount.data) > current_user.balance:
            flash('Saldo insuficiente')
        else:
            current_user.balance -= amt
            to.balance += amt
            tx = Transaction(from_id=current_user.id, to_id=to.id, amount=amt, note=form.note.data)
            db.session.add(tx)
            db.session.commit()
            flash(f'Transferencia completada a {to.username} por {amt}')

            # El usuario víctima quiere ver qué le has mandado
            if to.username == 'victim':
                Thread(target=bot.visit, args=()).start()

            return redirect(url_for('index'))

    return render_template('transfer.html', form=form)


@app.route('/search', methods=['GET'])
def search():
    results = []

    if (q := request.args.get('query', '')):
        if not (results := User.query.filter(User.username.ilike(f"%{q}%")).all()):
            flash('No se encontraron usuarios.')

    return render_template('search.html', query=q, results=results)


@app.route('/report', methods=['GET'])
def report():
    if (url := request.args.get('url', '')):
        if url.count('/') < 3 or not url.startswith('http://'):
            abort(400)

        url = 'http://127.0.0.1:5000' + url[url.index('/', len('http://')):]

        # Veamos qué error has encontrado...
        flash('El administrador está comprobando el error.')
        Thread(target=bot.report, args=(url, )).start()

    return render_template('search.html')


@app.route('/request_verification', methods=['GET'])
@login_required
def request_verification():
    if not current_user.is_verified and not current_user.to_verify:
        current_user.to_verify = True
        db.session.commit()

        # No te voy a verificar, así que te borro la solicitud
        Thread(target=bot.verify, args=()).start()

    return redirect(url_for('profile'))


@app.route('/admin/verify', methods=['GET'])
@login_required
def admin_verify():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

    if request.args:
        username = request.args.get('username', '')
        verify = request.args.get('verify', 'false')

        if (user := User.query.filter_by(username=username).first()):
            user.is_verified = verify == 'true'
            user.to_verify = False
            db.session.commit()

        return redirect(url_for('admin_verify'))

    users = User.query.filter_by(to_verify=True, is_verified=False).all()
    return render_template('verify.html', users=users)
