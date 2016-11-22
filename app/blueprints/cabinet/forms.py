from wtforms import Form, StringField, RadioField, SelectField, IntegerField, PasswordField, HiddenField, DecimalField,\
    validators, ValidationError


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


class BillingForm(Form):
    """Класс формы для пополнения баланса"""
    receiver = HiddenField('Receiver', [validators.DataRequired()])
    formcomment = HiddenField('Form comment', [validators.DataRequired()])
    shortdest = HiddenField('Short dest', [validators.DataRequired()])
    quickpayform = HiddenField('Quickpay form', [validators.DataRequired()], default='shop')
    targets = HiddenField('Targets', [validators.DataRequired()], default='Оплата услуг')
    paymentType = RadioField('Способ оплаты',  [validators.DataRequired()],
                             choices=(('PC', 'Яндекс.Деньгами'),
                                      ('AC', 'Банковской картой'),
                                      ('MC', 'С баланса мобильного')),
                             default='PC')
    sum = DecimalField('Сумма, руб.', [validators.DataRequired()], default=200)
    successURL = HiddenField('successURL', [validators.DataRequired()])
