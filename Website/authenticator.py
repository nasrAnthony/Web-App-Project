#imports
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from sqlalchemy import or_
from datetime import date #used to get Customer DOR. 
from .models import User, Employee, Hotel, Hotel_Chain, History
#from werkzeug.security import check_password_hash, generate_password_hash #will need these to secure the passwords. 
from . import db
import pickle

authenticator = Blueprint('authenticator', __name__)
@authenticator.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        email = request.form.get('email')
        userCust = User.query.filter_by(email=email).first() #get usert object. 
        empl = Employee.query.filter_by(email=email).first() #get employee object.
        if userCust: #check if user exists.
            if password == userCust.password:
                flash('Login successful!', category='success')
                login_user(userCust, remember=False) #save current user.
                userType = 'Customer'
                session['userType'] = 'Customer'
                return redirect(url_for('home_page.home')) #send user to home page after logging in.
            else:
                flash('Wrong password. Try again.', category='error')
        elif empl: #check if user is an employee. 
            if password == empl.password:
                flash('Login successful!', category='success')
                login_user(empl, remember=False) #save current user. 
                userType = 'Employee'
                session['userType'] = 'Employee'
                return redirect(url_for('home_page.home')) #send user to employee home page after logging in. 
            else:
                flash('Wrong password. Try again.', category='error')
        else:
            flash('Unregistered email. Please sign up instead.', category='error')

    return render_template('login.html')
 
#@authenticator.route('/')
#@login_required
#def home():
#    return redirect(url_for('views.home'))
#
#@authenticator.route('/home-employee')
#@login_required
#def home_employee():
#    return redirect(url_for('views.employeeHome'))

@authenticator.route("/logout")
@login_required
def logout():
    #logout the current user. 
    session.pop('userType', None)
    logout_user()
    return redirect((url_for('authenticator.login'))) #return over to the login screen when logged out.

def validateUser(email, passwordv1, passwordv2, fullName, ID, address, user, employee) -> bool: #method will return a tuple. (True, None)  if all is valid in the given fields. 
                                                #(False, string reason) if a problem is encountered. 
    #Validation:
    if user : #check if user exists
        return (False, "Email/ID is already in use by a customer account.")
    elif employee:
        return (False, "Email/ID is already in use by an employee account.")
    if len(email) < 4:
        return (False, "Email is too short. It must be at least 4 characters.")
    elif len(fullName) < 3: #meet the trigger implemented in database. 
        return (False, "Name is too short. It must be at least 3 characters.")
    elif passwordv1 != passwordv2:
        return (False, "Passwords do not match.")
    elif len(passwordv1) < 5:
        return (False, "Passwords is too short.")
    elif(len(str(ID)) <5):
        return (False, "Invalid SSN/SIN. ID is too short.")
    elif(10 < len(str(ID))):
        return (False, "Invalid SSN/SIN. ID is too long.")
    elif(len(address) < 5):
        return (False, "Address is too short. Please enter a valid address.")
    else:
        return (True, None)

def validateEmployee(email, passwordv1, passwordv2, fullName, ID, address, role, hotel, user, specific_hotel, employee) -> bool: #method will return a tuple. (True, None)  if all is valid in the given fields. 
                                                #(False, string reason) if a problem is encountered. 
    #Validation:
    #check if given hotel where employee works exists in db. 
    hotelSearch = Hotel.query.filter_by(hotel_ID=specific_hotel, hotel_chain_ID=hotel).first() #check if hotel exists in db
    #hotel_chain_search = Hotel_Chain.query.filter_by(hotel_chain_ID=hotel).first() #check if hotel chain exists in db
    if user: #check if user exists
        return (False, "Email/ID is already in use by a customer account.")
    elif employee:
        return (False, "Email is already in use by an employee account.")
    elif not(hotelSearch): #check if hotel not in db 
        return (False, "The hotel you work for is not supported by our services. Please register as a regular user.")
    elif len(email) < 4:
        return (False, "Email is too short. It must be at least 4 characters.")
    elif len(fullName) < 3: #meet the trigger implemented in database. 
        return (False, "Name is too short. It must be at least 3 characters.")
    elif passwordv1 != passwordv2:
        return (False, "Passwords do not match.")
    elif len(passwordv1) < 5:
        return (False, "Passwords is too short.")
    elif(len(str(ID)) <5):
        return (False, "Invalid SSN/SIN. ID is too short.")
    elif(10 < len(str(ID))):
        return (False, "Invalid SSN/SIN. ID is too long.")
    elif(len(address) < 5):
        return (False, "Address is too short. Please enter a valid address.")
    elif(len(role) <2):
        return (False, "Role is too short. Please enter a valid role.")
    elif(len(hotel) <2): #replace with a lookup into valid hotels!
        return (False, "Hotel chain given is invalid.")
    elif(len(specific_hotel) <2): #replace with a lookup into valid hotels!
        return (False, "Hotel given is invalid.")
    else:
        return (True, None)


@authenticator.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    available_roles = ['Manager', 'Clerk', 'Assistant']
    hotel_chains = Hotel_Chain.query.all()
    if request.method == 'POST':
        #fetching user info. 
        email = request.form.get('email')
        passwordv1 = request.form.get('passwordTemp')
        passwordv2 = request.form.get('password')
        full_name  = request.form.get('fullName')
        userID = request.form.get('userID')
        userDOR =  str(date.today()) #DOR
        address = request.form.get('address')
        userType = request.form.get('userType')
        #Validation:
        #user = User.query.filter_by(email=email).first()
        user = User.query.filter(or_(User.email==email, User.id == userID)).first()
        employee = Employee.query.filter(or_(Employee.email == email, Employee.id == userID)).first()
        if(str(userType) == "customer"):
            res = validateUser(email, passwordv1, passwordv2, full_name, userID, address, user, employee)
        if(str(userType) == "employee"):
            hotelChain = request.form.get('hotelChain')
            role = request.form.get('role')
            specific_hotel = request.form.get('specificHotel')
            res = validateEmployee(email, passwordv1, passwordv2, full_name, userID, address, role, hotelChain, user, specific_hotel, employee)
        reason = res[1]
        if(res[0] == True): #Validation has passed. 
            #print(res[0])
            #create new user send to db
            if(str(userType) == "customer"):
                current_user = User(email=email, full_name=full_name, id=userID, DOR=userDOR, password=passwordv2, address=address)
                db.session.add(current_user) #add user to database. 
                db.session.commit() #commit changes to server.
                #flash(f"Account created! DOR: {userDOR}", category='success') #show user account creation success message.
                login_user(current_user, remember=False) #save current user.  
                userType = 'Customer'
                flash(f"Account created! DOR: {userDOR}", category='success') #show user account creation success message.
                return redirect(url_for('home_page.home')) #send user to home page after sign up. 
            if(str(userType) == "employee"):
                current_user = Employee(email=email, full_name=full_name, id=userID, DOR=userDOR, password=passwordv2, address=address, hotel_chain_ID= hotelChain, hotel_ID = specific_hotel ,role =role )
                db.session.add(current_user) #add user to database. 
                db.session.commit() #commit changes to server.
                #flash(f"Account created! DOR: {userDOR}", category='success') #show user account creation success message.
                login_user(current_user, remember=False) #save current user.  
                userType = 'Employee'
                flash(f"Account created! DOR: {userDOR}", category='success') #show user account creation success message.
                return redirect(url_for('home_page.home')) #send employee user to employee page after sign up. 
        else: #Validation has failed
            flash(reason, category='error') #show user error message. 
    return render_template('signup.html', roles=  available_roles, chains= hotel_chains)

