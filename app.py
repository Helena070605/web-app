import os

from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from forms.new_problem import NewsForm
from data.problems import Problems
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager
from flask_login import login_required
from flask_login import logout_user
from flask_login import login_user
from flask_login import current_user
from flask import abort
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
# run_with_ngrok(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/problem')
def problem():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        problems = db_sess.query(Problems).filter(
            (Problems.user == current_user) | (Problems.is_private != True))
    else:
        problems = db_sess.query(Problems).filter(Problems.is_private != True)
    return render_template("problem.html", problems=problems)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            position=form.position.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/new_problem', methods=['GET', 'POST'])
@login_required
def new_problem():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        problems = Problems()
        problems.title = form.title.data
        problems.content = form.content.data
        problems.is_private = form.is_private.data
        current_user.problems.append(problems)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/problem')
    return render_template('add_problem.html', title='Добавление задачи',
                           form=form)


@app.route('/new_problem/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_problems(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        problems = db_sess.query(Problems).filter(Problems.id == id,
                                                  Problems.user == current_user
                                                  ).first()
        if problems:
            form.title.data = problems.title
            form.content.data = problems.content
            form.is_private.data = problems.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        problems = db_sess.query(Problems).filter(Problems.id == id,
                                                  Problems.user == current_user
                                                  ).first()
        if problems:
            problems.title = form.title.data
            problems.content = form.content.data
            problems.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/problem')
        else:
            abort(404)
    return render_template('add_problem.html',
                           title='Редактирование задачи',
                           form=form
                           )


@app.route('/problems_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def problems_delete(id):
    db_sess = db_session.create_session()
    problems = db_sess.query(Problems).filter(Problems.id == id,
                                              Problems.user == current_user
                                              ).first()
    if problems:
        db_sess.delete(problems)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/problem')


if __name__ == '__main__':
    db_session.global_init("db/base_workers.db")
    app.run()
