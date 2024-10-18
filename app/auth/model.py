from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash
from app import my_db as db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Document):
    meta = {"collection":"appUsers"}
    email = db.StringField()
    password = db.StringField()
    name = db.StringField()

    @staticmethod
    def getUser(email):
        return User.objects(email=email).first()
    
    @staticmethod
    def getUserById(user_id):
        return User.objects(pk=user_id).first()
    
    @staticmethod
    def createUser(email, name, password):
        # check if the user exist?
        user = User.getUser(email)
        if not user:
            user = User(
                email=email,
                name=name,
                password=generate_password_hash(password)
            )
            user.save()
        return user

    @staticmethod
    def checkPassword(hash, password):
        return check_password_hash(hash, password)

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


@login_manager.user_loader
def load_user(user_id):
    return User.getUserById(user_id)