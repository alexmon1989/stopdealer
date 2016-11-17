# Import flask and template operators
from flask import Flask, render_template, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_security import Security, MongoEngineUserDatastore, user_registered
from flask_admin import helpers as admin_helpers
from flask_mail import Mail
from flask_wtf.csrf import CsrfProtect
import datetime
from app.security.forms import ExtendedRegisterForm
from flask_babelex import Babel
from .models import db, Role, User
from app.admin import admin

# Объект mailer для импорта
mail = Mail()

user_datastore = MongoEngineUserDatastore(db, User, Role)


def create_app(**config_overrides):
    # Define the WSGI application object
    app = Flask(__name__)
    app.config.from_object('config')
    app.config.update(config_overrides)

    # CSRF
    if app.config.get('CSRF_ENABLED'):
        CsrfProtect(app)

    # Debugger
    if app.config.get('DEBUG'):
        if app.config.get('DEBUG_MONGO'):
            app.config['DEBUG_TB_PANELS'] = [
                'flask_debugtoolbar.panels.timer.TimerDebugPanel',
                'flask_mongoengine.panels.MongoDebugPanel'
            ]
        toolbar = DebugToolbarExtension(app)

    db.init_app(app)

    # Setup Flask-Security
    security = Security(app,
                        user_datastore,
                        confirm_register_form=ExtendedRegisterForm,
                        register_form=ExtendedRegisterForm)

    # Обработчик сигнала регистрации пользователя (высылает смс для подтверждения)
    @user_registered.connect_via(app)
    def when_user_registered(sender, user, confirm_token, **extra):
        print('User registered', user)

    # Mailer
    mail.init_app(app)

    # Babel
    babel = Babel(app)

    # Локализация (используется для русификации админ-панели)
    @babel.localeselector
    def get_locale():
        return 'ru'

    # Админ. панель
    admin.init_app(app)

    # define a context processor for merging flask-admin's template context into the
    # flask-security views.
    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    from .blueprints.home.controllers import home
    from .blueprints.blog.controllers import blog
    from .blueprints.about.controllers import about
    from .blueprints.contacts.controllers import contacts
    from .blueprints.prices.controllers import prices
    from .blueprints.cabinet.controllers import cabinet
    from .blueprints.phone.controllers import phone
    from .blueprints.automobile.controllers import automobile

    # Sample HTTP error handling
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    # Register blueprint(s)
    app.register_blueprint(home)
    app.register_blueprint(blog)
    app.register_blueprint(about)
    app.register_blueprint(contacts)
    app.register_blueprint(prices)
    app.register_blueprint(cabinet)
    app.register_blueprint(phone)
    app.register_blueprint(automobile)

    @app.context_processor
    def my_utility_processor():

        def date_now(format="%d.m.%Y %H:%M:%S"):
            """ returns the formated datetime """
            return datetime.datetime.now().strftime(format)

        return dict(date_now=date_now)

    return app
