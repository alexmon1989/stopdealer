from flask_security.forms import RegisterForm, Required
from wtforms import StringField


class ExtendedRegisterForm(RegisterForm):
    """Переопределение формы регистрации"""
    username = StringField('Ваше имя', [Required(message='Введите ваше имя')])
