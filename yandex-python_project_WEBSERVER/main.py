from flask import Flask, render_template, redirect, request, make_response
from data import db_session
from login_form import LoginForm
from data.users import User
from data.tasks import Tasks
from Forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
n = 9


@app.route('/')
def main_page():
    dict_param = {'title': 'Main page'}
    return render_template('base.html', **dict_param)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/task/0")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/task/<int:id>', methods=['GET', 'POST'])
@login_required
def task(id):
    if id == n:
        return render_template('end.html')
    correctness = ''
    answer = ''
    id = int(id)
    id += 1
    if request.method == 'POST':
        answer = request.form['answer']
    db_sess = db_session.create_session()
    task1 = db_sess.query(Tasks).filter(Tasks.id == id)
    if answer != '':
        if answer == db_sess.query(Tasks).filter(Tasks.id == id).first().answer:
            correctness = "Верно"
        else:
            correctness = 'Неверно'
    return render_template('task.html', tasks=task1, form=task, correctness=correctness, id=id)


@app.route('/next_task', methods=['GET', 'POST'])
def next_task():
    curId = int(request.cookies.get("curId", 1))
    res = make_response(f"Задача{curId + 1}")
    res.set_cookie('curId', str(curId + 1), max_age=60 * 60 * 24 * 365 * 2)
    task()


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
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/tasks.db")
    app.run()


if __name__ == '__main__':
    main()