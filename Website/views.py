#imports
from flask import Blueprint, render_template
from flask_login import login_user, login_required, logout_user, current_user
#from .authenticator import userType

views = Blueprint('views', __name__)

@views.route("/", methods=['GET', 'POST'])#decorator
@login_required
def home():
    #print(userType)
    #if userType == 'Customer':
    #    return render_template('home.html')
    #else:
    #    if(userType is None):
    #        return render_template('login.html')
    return render_template('home.html')

@views.route("/home-employee", methods=['GET', 'POST'])#decorator
@login_required
def employeeHome():
    #if userType == 'Employee':
    #    return render_template('employee_home.html')
    #else:
    #    if(userType is None):
    #        return render_template('login.html')
    return render_template('employee_home.html')

