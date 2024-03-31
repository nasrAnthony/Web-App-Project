from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from . import db
from .models import Hotel, Hotel_Chain, Room, Booking, User, Employee, Renting, History, HotelTotalCapacity
import pickle
from .searchEngine import validate_booking, validate_booking_with_rentings
import time

display_profile = Blueprint('profile', __name__)

@display_profile.route("/profile", methods=['GET', 'POST'])
@login_required
def customer_profile():
    #offer editing profile attributes?
    #fetch all the bookings the current customer has created. 
    customer_bookings = Booking.query.filter_by(customer_ID= current_user.id).all() 
    customer_rentings = Renting.query.filter_by(customer_ID= current_user.id).all()
    #for booking in customer_bookings:
    #    print(booking.booking_ID, booking.room_ID, booking.hotel_ID, booking.length_stay, booking.start_date, booking.end_date)
    
    return render_template('profile.html', name = current_user.full_name, id = current_user.id, address = current_user.address, 
                                        DOR = current_user.DOR, bookings = customer_bookings, rentings = customer_rentings)
    #return render_template('profile.html')

@display_profile.route("/profile-employee", methods=['GET', 'POST'])
@login_required
def employee_profile():
    #for booking in hotel_bookings:
    #    print(booking)
    #    print(type(booking), type(hotel_bookings[0]))
    #    print(booking.booking_ID)
    #let the employee see the bookings for the hotel they work for. 
    hotel_bookings = Booking.query.filter_by(hotel_ID= current_user.hotel_ID).all()
    hotel_rentings = Renting.query.filter_by(hotel_ID= current_user.hotel_ID).all()
    history_bookings = pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_bookings)
    history_rentings =  pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_rentings)
    available_rooms = Room.query.filter_by(hotel_ID = current_user.hotel_ID).all()
    capacity = HotelTotalCapacity.query.filter_by(hotel_ID =current_user.hotel_ID).first()
    #print(capacity)
   #for renting in history_rentings:
   #   print(renting, renting.room_ID)
    return render_template('employee_profile.html',name = current_user.full_name, id = current_user.id, address = current_user.address, 
                           DOR = current_user.DOR, hotel = current_user.hotel_ID, hotel_Chain= current_user.hotel_chain_ID, 
                           role= current_user.role, bookings = hotel_bookings, rentings = hotel_rentings, booking_history = history_bookings, 
                           rentings_history = history_rentings, list_rooms = available_rooms, hotel_capacity= capacity )

@display_profile.route("/profile/delete-booking/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def delete_booking(booking_id):
    Booking.query.filter_by(booking_ID = booking_id).delete()
    db.session.commit()
    customer_bookings = Booking.query.filter_by(customer_ID= current_user.id).all()  #update list of bookings post delete. 
    customer_rentings = Renting.query.filter_by(customer_ID= current_user.id).all()
    flash('Booking deleted!', category='success')
    return render_template('profile.html', name = current_user.full_name, id = current_user.id, address = current_user.address, 
                           DOR = current_user.DOR, bookings = customer_bookings,rentings = customer_rentings)


@display_profile.route("/profile-employee/delete-booking/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def employee_delete_booking(booking_id):
    Booking.query.filter_by(booking_ID = booking_id).delete()
    db.session.commit()
    hotel_bookings = Booking.query.filter_by(hotel_ID= current_user.hotel_ID).all()  #update list of bookings post delete. 
    hotel_rentings = Renting.query.filter_by(hotel_ID= current_user.hotel_ID).all()
    available_rooms = Room.query.filter_by(hotel_ID = current_user.hotel_ID).all()
    flash('Booking deleted!', category='success')
    #employee_profile()
    history_bookings = pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_bookings)
    history_rentings =  pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_rentings)
    capacity = HotelTotalCapacity.query.filter_by(hotel_ID =current_user.hotel_ID).first()
    return render_template('employee_profile.html',name = current_user.full_name, id = current_user.id, address = current_user.address, 
                          DOR = current_user.DOR, hotel = current_user.hotel_ID, hotel_Chain= current_user.hotel_chain_ID, 
                          role= current_user.role, bookings = hotel_bookings, rentings = hotel_rentings, booking_history = history_bookings, 
                          rentings_history = history_rentings, list_rooms = available_rooms, hotel_capacity= capacity)

def validate_payment(card_number, card_cvc):
    #print(card_number, card_cvc)
    #print(len(str(card_number)), len(str(card_cvc)))
    if(len(str(card_number)) != 16):
            return (False, 'Payment failed: Card number is invalid.')
    elif(len(str(card_cvc))!=3):
        return (False, 'Payment failed: Card CVC is invalid.')
    else:
        return (True, '')

@display_profile.route("/profile-employee/check-in/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def employee_check_in(booking_id):
    if request.method == 'POST':
        card_number = request.form.get('card_number_checkin')
        card_cvc = request.form.get('card_cvc_checkin')
        is_pay_valid = validate_payment(card_number, card_cvc)
        if(is_pay_valid[0]):
            #mehtod to check in a customer with a prior booking. 
            #when a renting is to be created from a booking, all the information of the booking is used to create th renting.
            booking = Booking.query.filter_by(booking_ID= booking_id).first()
            #create a renting from the booking info. 
            customer = User.query.filter_by(id=booking.customer_ID).first()
            room = Room.query.filter_by(room_ID=booking.room_ID).first()
            available_rooms = Room.query.filter_by(hotel_ID = current_user.hotel_ID).all()
            history = History.query.filter_by(hotel_ID= current_user.hotel_ID).first() #find the history associated with the hotel. 
            new_renting = Renting(renting_ID= booking.booking_ID, start_of_stay= booking.start_date, end_of_stay= booking.end_date, 
                                customer_ID= booking.customer_ID, hotel_chain_ID= booking.hotel_chain_ID, hotel_ID= booking.hotel_ID, 
                                room_ID= booking.room_ID, list_bookings= booking.list_bookings, list_rentings= booking.list_rentings, room=room, customer=customer)
            #we will commit the renting to the renting table, then delete the booking, as it is no longer needed. 
            db.session.add(new_renting)
            Booking.query.filter_by(booking_ID = booking_id).delete()
            hotel_bookings = Booking.query.filter_by(hotel_ID= current_user.hotel_ID).all()  #update list of bookings post delete./renting creation. 
            hotel_rentings = Renting.query.filter_by(hotel_ID= current_user.hotel_ID).all()
            list_rentings = pickle.loads(history.list_rentings) 
            #print("HERE", list_rentings)
            list_rentings.append(new_renting)
            history.list_rentings = pickle.dumps(list_rentings)
            db.session.add(history)
            db.session.commit()
            history_bookings = pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_bookings)
            history_rentings =  pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_rentings)
            capacity = HotelTotalCapacity.query.filter_by(hotel_ID =current_user.hotel_ID).first()
            flash('Customer has been checked in, a renting has replaced the booking!', category='success')
            return render_template('employee_profile.html',name = current_user.full_name, id = current_user.id, address = current_user.address, 
                                   DOR = current_user.DOR, hotel = current_user.hotel_ID, hotel_Chain= current_user.hotel_chain_ID, 
                                   role= current_user.role, bookings = hotel_bookings, rentings = hotel_rentings, booking_history = history_bookings,
                                     rentings_history = history_rentings, list_rooms = available_rooms, hotel_capacity= capacity)
        if(not(is_pay_valid[0])):
            #mehtod to check in a customer with a prior booking. 
            #when a renting is to be created from a booking, all the information of the booking is used to create th renting.
            booking = Booking.query.filter_by(booking_ID= booking_id).first()
            #create a renting from the booking info. 
            customer = User.query.filter_by(id=booking.customer_ID).first()
            room = Room.query.filter_by(room_ID=booking.room_ID).first()
            available_rooms = Room.query.filter_by(hotel_ID = current_user.hotel_ID).all()
            history = History.query.filter_by(hotel_ID= current_user.hotel_ID).first() #find the history associated with the hotel.
            hotel_bookings = Booking.query.filter_by(hotel_ID= current_user.hotel_ID).all()  #update list of bookings post delete./renting creation. 
            hotel_rentings = Renting.query.filter_by(hotel_ID= current_user.hotel_ID).all()
            history_bookings = pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_bookings)
            history_rentings =  pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_rentings)
            flash(is_pay_valid[1], category='error')
            capacity = HotelTotalCapacity.query.filter_by(hotel_ID =current_user.hotel_ID).first()
            return render_template('employee_profile.html',name = current_user.full_name, id = current_user.id, address = current_user.address, 
                                   DOR = current_user.DOR, hotel = current_user.hotel_ID, hotel_Chain= current_user.hotel_chain_ID, 
                                   role= current_user.role, bookings = hotel_bookings, rentings = hotel_rentings, booking_history = history_bookings,
                                     rentings_history = history_rentings, list_rooms = available_rooms, hotel_capacity= capacity)

@display_profile.route("/profile-employee/delete-renting/<int:renting_id>", methods=['GET', 'POST'])
@login_required
def employee_delete_renting(renting_id):
    Renting.query.filter_by(renting_ID = renting_id).delete()
    db.session.commit()
    hotel_bookings = Booking.query.filter_by(hotel_ID= current_user.hotel_ID).all()  #update list of bookings post delete. 
    hotel_rentings = Renting.query.filter_by(hotel_ID= current_user.hotel_ID).all()
    available_rooms = Room.query.filter_by(hotel_ID = current_user.hotel_ID).all()
    flash('Renting deleted!', category='success') 
    history_bookings = pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_bookings)
    history_rentings =  pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_rentings)
    capacity = HotelTotalCapacity.query.filter_by(hotel_ID =current_user.hotel_ID).first()
    return render_template('employee_profile.html',name = current_user.full_name, id = current_user.id, address = current_user.address, 
                         DOR = current_user.DOR, hotel = current_user.hotel_ID, hotel_Chain= current_user.hotel_chain_ID, 
                         role= current_user.role, bookings = hotel_bookings, rentings = hotel_rentings, booking_history = history_bookings,
                           rentings_history = history_rentings, list_rooms = available_rooms, hotel_capacity= capacity)

def validate_renting(customer_ID, room_ID, start_date, end_date, card_number, card_cvc):
    #check if selected room exists within hotel. 
    room_check = Room.query.filter_by(hotel_ID = current_user.hotel_ID, room_ID= room_ID).first()
    if not(room_check): #room is not found within the rooms table associated with hotel the customer is employed by. 
        return (False, 'Failed to create renting. Room number is invalid.')
    #must check if the dates conflict with another booking/renting already in the database.
    if room_check: #if room exists. Check date issues...
        is_valid_booking = validate_booking(room_ID, current_user.hotel_ID, start_date, end_date)
        is_valid_renting = validate_booking_with_rentings(room_ID, current_user.hotel_ID, start_date, end_date)
        if(not(is_valid_booking[0]) or not(is_valid_renting[0])): #renting is conflicting with a another booking/renting at the hotel with this room. 
            return (False, 'Failed to create renting. Time conflict another booking/renting.')
        elif(is_valid_booking[0] or is_valid_renting[0]):
            if(len(str(card_number)) != 16):
                return (False, 'Payment failed: Card number is invalid.')
            elif(len(str(card_cvc))!=3):
                return (False, 'Payment failed: Card CVC is invalid.')
            else:
                return (True, '')
        

@display_profile.route("/profile-employee/create-renting", methods=['GET', 'POST'])
@login_required
def employee_create_renting():
    if request.method == 'POST':
        customer_ID = request.form.get('customerID')
        room_ID = request.form.get('roomID')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        #payment details:
        card_number = request.form.get('card_number')
        card_cvc = request.form.get('card_cvc')
        res = validate_renting(customer_ID, room_ID, start_date, end_date, card_number, card_cvc)

    if res[0] == True:
        hotel_bookings = Booking.query.filter_by(hotel_ID= current_user.hotel_ID).all()  
        hotel_rentings = Renting.query.filter_by(hotel_ID= current_user.hotel_ID).all()
        #fetch room. 
        #check if customer exists. It is possible a customer shows up physically to start a renting without having an account on the web app!
        customer = User.query.filter_by(id=customer_ID).first()
        if(not(customer)): #if no customer account is detected with this ID, a mock temporary account is created with all attributes set to "temp" which can be deleted once the renting is done. 
            renting_ID = abs(int(current_user.id - int(time.time()))) #creating a unique renting id as a mix of employee id and current time at creation of renting. 
            temp_account = User(email=f'renting{str(renting_ID)}@{current_user.hotel_ID}.com', full_name='Rent User', id=customer_ID, DOR=str(start_date), password='renting', address='Rent') #will associate this account to the renting.
            db.session.add(temp_account) #add temporary user to database. 
            room = Room.query.filter_by(hotel_ID= current_user.hotel_ID, room_ID= room_ID).first()
            hotel_chain_ID = current_user.hotel_chain_ID
            new_renting = Renting(renting_ID= renting_ID, start_of_stay=start_date, end_of_stay=end_date, 
                        customer_ID= customer_ID, hotel_chain_ID= hotel_chain_ID, hotel_ID= current_user.hotel_ID, 
                        room_ID= room_ID, list_bookings= [], list_rentings= [], room=room, customer=temp_account)

        elif(customer):
            room = Room.query.filter_by(hotel_ID= current_user.hotel_ID, room_ID= room_ID).first()
            hotel_chain_ID = current_user.hotel_chain_ID
            renting_ID = abs(int(current_user.id - int(time.time()))) #creating a unique renting id as a mix of employee id and current time at creation of renting. 
            new_renting = Renting(renting_ID= renting_ID, start_of_stay=start_date, end_of_stay=end_date, 
                        customer_ID= customer_ID, hotel_chain_ID= hotel_chain_ID, hotel_ID= current_user.hotel_ID, 
                        room_ID= room_ID, list_bookings= [], list_rentings= [], room=room, customer=customer)
            
        db.session.add(new_renting)
        #
        flash('Renting created!', category='success') 
        history = History.query.filter_by(hotel_ID= current_user.hotel_ID).first() #find the history associated with the hotel. 
        history_bookings = pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_bookings)
        history_rentings =  pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_rentings)
        list_rentings = pickle.loads(history.list_rentings) 
        #print("HERE", list_rentings)
        list_rentings.append(new_renting)
        history.list_rentings = pickle.dumps(list_rentings)
        #print("HERE", current_user.hotel_ID, list_rentings)
        db.session.add(history)
        db.session.commit()

    if(res[0] == False):
        hotel_bookings = Booking.query.filter_by(hotel_ID= current_user.hotel_ID).all()  
        hotel_rentings = Renting.query.filter_by(hotel_ID= current_user.hotel_ID).all()
        flash(res[1], category='error') 
        history_bookings = pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_bookings)
        history_rentings =  pickle.loads(History.query.filter_by(hotel_ID = current_user.hotel_ID).first().list_rentings)

    available_rooms = Room.query.filter_by(hotel_ID = current_user.hotel_ID).all()
    capacity = HotelTotalCapacity.query.filter_by(hotel_ID =current_user.hotel_ID).first()
    return render_template('employee_profile.html',name = current_user.full_name, id = current_user.id, address = current_user.address, 
                         DOR = current_user.DOR, hotel = current_user.hotel_ID, hotel_Chain= current_user.hotel_chain_ID, 
                         role= current_user.role, bookings = hotel_bookings, rentings = hotel_rentings, booking_history = history_bookings, 
                         rentings_history = history_rentings, list_rooms = available_rooms, hotel_capacity= capacity)








