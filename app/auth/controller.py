from auth import auth
from flask import redirect, url_for, request, render_template, flash
from flask_login import login_user, logout_user, current_user
from auth.model import LoginForm, User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('book.packages'))
    form = LoginForm()
    if form.validate_on_submit():
        # if request.method == 'POST' and form.validate():
        # email = request.form.get('email')
        # password = request.form.get('pswd')
        # remember = request.form.get('remember')
        check_user = User.getUser(form.email.data)
        if not check_user:
            form.email.errors.append("email not found")
            return render_template("login.html", form=form)
            # also need check 
        elif not check_user.checkPassword(check_user.password, form.password.data):
            form.password.errors.append("password incorrect")
            return render_template("login.html", form=form)
        else:
            login_user(check_user, remember=form.remember.data)
            flash("you are logged in")
            return redirect(url_for('book.packages'))

    return render_template("login.html", form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route("/registration", methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email')
        pswd = request.form.get('pswd')
        name = request.form.get('name')
        User.createUser(email, name, pswd)
        return render_template('registration.html')

    if request.method == 'GET':
        return render_template('registration.html')