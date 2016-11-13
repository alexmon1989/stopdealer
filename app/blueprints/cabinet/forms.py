from wtforms import Form, StringField, SelectField, IntegerField, PasswordField, validators, ValidationError


class DetailsForm(Form):
    """Класс формы для редактирования деталей профиля"""
    username = StringField('Имя', [validators.Length(min=3, max=60)])
    email = StringField('Email', [validators.Email()])
    password = PasswordField('Пароль', [
        validators.Optional(),
        validators.Length(min=6)
    ])
    confirm_password = PasswordField('Подтверждение пароля', [
        validators.EqualTo(fieldname='password', message='Пароли не совпадают')
    ])


class CheapenedAutosForm(Form):
    """Класс формы для поиска подешевевших авто"""
    manufacturer = SelectField('Марка', [validators.Length(min=3, max=60)])
    model = SelectField('Модель', [validators.Length(min=3, max=60)])
    year_from = SelectField('От', [])
    year_to = SelectField('До', [],)
    fell_by_from = IntegerField('От')
    fell_by_to = IntegerField('До')
    fell_by_date_from = StringField('От')
    fell_by_date_to = StringField('До')


def my_above_zero(form, field):
    """Проверяет значение поля (должно быть положительным)"""
    if int(field.data.replace(' ', '')) < 1:
        raise ValidationError('Значение поля не может быть меньше 1.')


class DeliveryForm(Form):
    """Класс формы для создания рассылки"""
    manufacturer = SelectField('Марка', [validators.DataRequired(), validators.Length(min=3, max=60)])
    model = SelectField('Модель', [validators.DataRequired()])
    year_from = SelectField('От', [validators.DataRequired()])
    year_to = SelectField('До', [validators.DataRequired()])
    price_from = StringField('Цена от', [validators.DataRequired(), my_above_zero])
    price_to = StringField('Цена до', [validators.DataRequired(), my_above_zero])
    transmission = SelectField('КПП', [validators.Optional()], choices=(('', 'Любая'),
                                                                        ('механика', 'Механика'),
                                                                        ('автомат', 'Автомат'),
                                                                        ('роботизированная', 'Роботизированная'),
                                                                        ('вариатор', 'Вариатор')))

