#imports
from flask import Flask
from getpass import getpass
from mysql.connector import connect, Error
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists
from flask_login import LoginManager, logout_user
import pickle

db = SQLAlchemy()

#mysql://tony:Aliame123@server/db
def init_application(): #initialize the application and instanciate Flask module. 
    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'Yeet meow' #completely random not needed.
    application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tony:Aliame123@localhost/eHotelsDB'
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(application)
    from .models import User, Hotel_Chain, Hotel, Room, History, Renting, Booking, Employee, AvailableRoomsPerArea  #import models for table creation.
    #import blueprints
    #from .models import User, Hotel_Chain, Hotel, Room, History, Renting, Booking, Employee  #import models for table creation.
    from .views import views
    from .home import home_page
    from .authenticator import authenticator
    from .searchEngine import search_engine
    from .profile import display_profile
    if(database_exists('mysql+pymysql://tony:Aliame123@localhost/eHotelsDB')):
        print('Database already exists!')
    else:
        with application.app_context():
            db.create_all() #create the tables in the database, but won't update the :
            print('Database not found. A new one was created!')
    login_manager = LoginManager()
    login_manager.login_view = 'authenticator.login'
    login_manager.init_app(application)
    @login_manager.user_loader
    def load_user(id):
        if(Employee.query.get(int(id)) is None):
            return User.query.get(int(id))
        else:
            return Employee.query.get(int(id))

    #@login_manager.user_loader
    #def load_employee(id):
    #    return Employee.query.get(int(id))
    #register the blueprint
    application.register_blueprint(home_page, url_prefix='/') #no prefix
    application.register_blueprint(authenticator, url_prefix='/') #no prefix
    application.register_blueprint(search_engine, url_prefix='/') #no prefix
    application.register_blueprint(display_profile, url_prefix='/') #no prefix
    return application


