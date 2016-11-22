import datetime
from flask_security import UserMixin, RoleMixin
from werkzeug.contrib.cache import SimpleCache
from flask_mongoengine import MongoEngine


db = MongoEngine()

# Cache
cache = SimpleCache()


class Automobile(db.Document):
    e1_id = db.IntField(required=True)
    props = db.ListField(db.StringField())
    seller = db.ListField(db.StringField())
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {'collection': 'automobiles'}

    @staticmethod
    def get_seller_phones_count():
        """Взвращает список телефонов продавцов"""
        res = cache.get('seller-phones')
        if res is None:
            res = len(Automobile.objects(seller__phone__ne=None).distinct('seller.phone'))
            cache.set('seller-phones', res, timeout=24*60*60)
        return res

    def get_price(self):
        """Возвращает цену авто"""
        price = Price.objects(automobile=self).first()
        if price:
            return price.value
        else:
            return 0


class Page(db.Document):
    slug = db.StringField(max_length=255, unique=True)
    title = db.StringField(max_length=255)
    content = db.StringField()
    head_title = db.StringField(max_length=255)
    meta_description = db.StringField(default="")
    meta_keywords = db.StringField(default="")
    contact_form_email = db.StringField(max_length=255, default=None)
    contact_widget_content = db.StringField(default=None)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'pages',
        'indexes': ['slug']
    }


class Blog(db.Document):
    slug = db.StringField(max_length=255, unique=True)
    title = db.StringField(max_length=255)
    content = db.StringField()
    visits = db.IntField(default=0)
    head_title = db.StringField(max_length=255)
    meta_description = db.StringField(max_length=255, default="")
    meta_keywords = db.StringField(max_length=255, default="")
    enabled = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': ['slug']
    }


class Price(db.Document):
    automobile = db.ReferenceField('Automobile')
    value = db.IntField('value')
    mileage = db.StringField('mileage')
    automobile_props = db.ListField(db.StringField())
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'prices',
        'indexes': ['automobile']
    }


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

    meta = {
        'collection': 'roles'
    }

    def __str__(self):
        return self.description


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255, unique=True)
    username = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    balance = db.DecimalField(min_value=0, default=0)
    active = db.BooleanField(default=False)
    confirmed_at = db.DateTimeField()
    current_login_at = db.DateTimeField()
    current_login_ip = db.StringField(max_length=255)
    last_login_ip = db.StringField(max_length=255)
    last_login_at = db.DateTimeField(max_length=255)
    login_count = db.IntField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'users'
    }

    def __str__(self):
        return self.email


class Search(db.Document):
    phone = db.StringField()
    user = db.ReferenceField(User)
    success = db.BooleanField(default=False)
    last_automobile = db.ReferenceField(Automobile, default=None)
    created_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'searches'
    }


class CheapenedAuto(db.Document):
    """Модель отвечает за взаимодействие с коллекцией *cheapened_autos*

    Атрибуты:
    - automobile: поле документа, данные автомобиля, по сути копия документа из коллекции *automobiles*
    - fell_by: поле документа, значение насколько подешевело авто
    - created_at: поле документа, время создания записи
    """
    automobile = db.ListField(db.StringField())
    fell_by = db.IntField()
    created_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'cheapened_autos'
    }


class AutomobileManufacturer(db.Document):
    """Модель отвечает за взамодействие с коллекцией *automobile_manufacturers*

    Атрибуты:
    - title: поле документа, название производителя авто
    - created_at: поле документа, время создания записи
    - updated_at: поле документа, время изменения записи
    """
    title = db.StringField(max_length=255, unique=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'automobile_manufacturers'
    }


class Delivery(db.Document):
    """Модель отвечает за взамодействие с коллекцией *deliveries* (подписки пользователей на рассылку)

    Атрибуты:
    - user_id: id пользователя, создавшего запись
    - manufacturer: производитель авто
    - model: модель авто
    - year_from: год производства от
    - year_to: год производства до
    - price_from: цена от
    - price_to: цена до
    - transmission: тип коробки передач
    - enabled: включена ли рассылка
    - last_letter_at: последния отправка письма по этой рассылке
    - created_at: поле документа, время создания записи
    - updated_at: поле документа, время изменения записи
    """
    user_id = db.ReferenceField(User)
    manufacturer = db.StringField()
    model = db.StringField()
    year_from = db.StringField()
    year_to = db.StringField()
    price_from = db.IntField()
    price_to = db.IntField()
    transmission = db.StringField()
    enabled = db.BooleanField(default=True)
    last_letter_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'deliveries'
    }


class Order(db.Document):
    """Модель отвечает за взамодействие с коллекцией *orders* (оплаты)

    Атрибуты:
    - sum: сумма заказа
    - user: id пользователя, создавшего заказ
    - paid_at: время оплаты заказа
    - created_at: поле документа, время создания записи
    """
    sum = db.DecimalField(required=True, min_value=0)
    user = db.ReferenceField(User, required=True)
    paid_at = db.DateTimeField()
    created_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'orders'
    }

    def mark_paid(self):
        """Помечает заказ как оплаченный."""
        self.paid_at = datetime.datetime.now
        self.save()
