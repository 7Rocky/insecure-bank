from flask_wtf import FlaskForm

from wtforms import DecimalField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import EqualTo, InputRequired, Length, NumberRange


class EditProfileForm(FlaskForm):
    bio = TextAreaField('Biografía', validators=[Length(max=500)])
    submit = SubmitField('Guardar cambios')


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[InputRequired()])
    password = PasswordField('Contraseña', validators=[InputRequired()])
    submit = SubmitField('Entrar')


class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[InputRequired(), Length(min=3, max=80)])
    password = PasswordField('Contraseña', validators=[InputRequired(), Length(min=6)])
    password2 = PasswordField('Repetir contraseña', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')


class TransferForm(FlaskForm):
    class Meta:
        csrf = False

    to_username = StringField('Enviar a', validators=[InputRequired()])
    amount = DecimalField('Cantidad', places=2, validators=[InputRequired(), NumberRange(min=0.01)])
    note = TextAreaField('Nota (opcional)')
    submit = SubmitField('Transferir')
