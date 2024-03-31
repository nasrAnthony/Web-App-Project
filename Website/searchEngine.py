from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from . import db
from .models import Hotel, Hotel_Chain, Room, Booking, Renting, History, Employee
from datetime import datetime
from collections import namedtuple
import time, pickle

search_engine = Blueprint('search', __name__)

selected_hotel = ""
display_results = False

@search_engine.route("/search/<string:location>", methods=['GET', 'POST'])
@login_required
def search_from_home(location):
    display_results = True
    hotel_results = Hotel.query.filter(Hotel.address.like('%'+location+'%')).all()
    return render_template('search.html', hotels = hotel_results, display_results = display_results)

@search_engine.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST': #need to add more ways of searching (example: by location, city...)
        display_results = True
        target_hotel_ID = request.form.get('hotelChainName')
        target_city = request.form.get('location')
        if(len(target_hotel_ID)==0 and len(target_city)==0): #if no filters are given. Simply show all possible hotels. 
            hotel_results = Hotel.query.all()
        elif(len(target_city)==0 and len(target_hotel_ID)!=0 ): #search based hotel_ID
            hotel_results = Hotel.query.filter_by(hotel_chain_ID = target_hotel_ID).all()#all hotels belonging to specific chain.
        elif(len(target_city)!=0 and len(target_hotel_ID)==0 ): #search based on city
            hotel_results = Hotel.query.filter(Hotel.address.like('%'+target_city+'%')).all()
        elif(len(target_city)!=0 and len(target_hotel_ID)!=0 ): #search based on both (city and hotel_ID).
            hotel_results = Hotel.query.filter(Hotel.hotel_chain_ID == target_hotel_ID , Hotel.address.like('%'+target_city+'%')).all()
        return render_template('search.html', hotels = hotel_results, display_results = display_results)
    return render_template('search.html')

def user_is_employee() -> bool: #will check if the current user is found in the employee table by checking the PK id. 
    is_employee = Employee.query.filter_by(id= current_user.id).first()
    #$print(current_user.id, current_user.full_name, is_employee)
    if(is_employee): #check if current used is an employee
        return True
    else:
        return False

@search_engine.route("/see_rooms/<string:hotel_id>", methods=['GET'])
@login_required
def see_rooms(hotel_id):
    #hotel_rooms = []
    room_results = Room.query.filter_by(hotel_ID = hotel_id).all()#all rooms belonging to a specific hotel. 
    #print(hotel_id)
    #print(room_results)
    return render_template('rooms.html', rooms = room_results, hotel_id = hotel_id)

def validate_booking(room_id, hotel_id, start_date, end_date): #mehtod will query the db to look for other conflicting bookings!
                                                                #returns true if no conflicts, returns false otherwise. 
    Range = namedtuple('Range', ['start', 'end'])
    #building initial time range:
    start_year = int(start_date.split('-')[0])
    start_month = int(start_date.split('-')[1])
    start_day = int(start_date.split('-')[2])
    end_year = int(end_date.split('-')[0])
    end_month = int(end_date.split('-')[1])
    end_day = int(end_date.split('-')[2])
    time_range1 = Range(start=datetime(start_year, start_month, start_day), end=datetime(end_year, end_month, end_day))
    num_days = time_range1.end-time_range1.start
    #print(start_year, start_month, start_day)
    #print(end_year,  end_month, end_day)
    potential_conflict_bookings = Booking.query.filter_by(hotel_ID = hotel_id, room_ID = room_id).all() #get all bookings for the target room
    for booking in potential_conflict_bookings: #loop through the bookings fetched. 
        start_date2 = booking.start_date #get potential conflicting booking times
        end_date2 = booking.end_date
        start_year2 = int(start_date2.split('-')[0])
        start_month2 = int(start_date2.split('-')[1])
        start_day2 = int(start_date2.split('-')[2])
        end_year2 = int(end_date2.split('-')[0])
        end_month2 = int(end_date2.split('-')[1])
        end_day2 = int(end_date2.split('-')[2])
        time_range2 = Range(start=datetime(start_year2, start_month2, start_day2), end=datetime(end_year2, end_month2, end_day2))
        latest_start = max(time_range1.start, time_range2.start)
        earliest_end = min(time_range1.end, time_range2.end)
        difference = (earliest_end - latest_start).days + 1
        number_overlapping_days = max(0,difference) #will be 0 or the number shown by difference. 
        #print(number_overlapping_days)
        if(number_overlapping_days!=0):
            return (False, 0)
    return (True, num_days.days)

def validate_booking_with_rentings(room_id, hotel_id, start_date, end_date): #mehtod will query the db to look for other conflicting bookings!
                                                                #returns true if no conflicts, returns false otherwise. 
    Range = namedtuple('Range', ['start', 'end'])
    #building initial time range:
    start_year = int(start_date.split('-')[0])
    start_month = int(start_date.split('-')[1])
    start_day = int(start_date.split('-')[2])
    end_year = int(end_date.split('-')[0])
    end_month = int(end_date.split('-')[1])
    end_day = int(end_date.split('-')[2])
    time_range1 = Range(start=datetime(start_year, start_month, start_day), end=datetime(end_year, end_month, end_day))
    num_days = time_range1.end-time_range1.start
    #print(start_year, start_month, start_day)
    #print(end_year,  end_month, end_day)
    potential_conflict_bookings = Renting.query.filter_by(hotel_ID = hotel_id, room_ID = room_id).all() #get all bookings for the target room
    for renting in potential_conflict_bookings: #loop through the bookings fetched. 
        start_date2 = renting.start_of_stay #get potential conflicting renting times
        end_date2 = renting.end_of_stay #get potential conflicting renting times
        start_year2 = int(start_date2.split('-')[0])
        start_month2 = int(start_date2.split('-')[1])
        start_day2 = int(start_date2.split('-')[2])
        end_year2 = int(end_date2.split('-')[0])
        end_month2 = int(end_date2.split('-')[1])
        end_day2 = int(end_date2.split('-')[2])
        time_range2 = Range(start=datetime(start_year2, start_month2, start_day2), end=datetime(end_year2, end_month2, end_day2))
        latest_start = max(time_range1.start, time_range2.start)
        earliest_end = min(time_range1.end, time_range2.end)
        difference = (earliest_end - latest_start).days + 1
        number_overlapping_days = max(0,difference) #will be 0 or the number shown by difference. 
        #print(number_overlapping_days)
        if(number_overlapping_days!=0):
            return (False, 0)
    return (True, num_days.days)

def populate_history():
    hotels = Hotel.query.all()
    for hotel in hotels:
        list_rentings = pickle.dumps([])
        list_bookings = pickle.dumps([])
        new_history = History(hotel_ID=str(hotel.hotel_ID), hotel_chain_ID=str(hotel.hotel_chain_ID), 
                      list_rentings=list_rentings, list_bookings=list_bookings)
        db.session.add(new_history)
        db.session.commit()

@search_engine.route("/see_rooms/<string:hotel_id>/book/room-<string:room_id>", methods=['GET', 'POST'])
@login_required
def see_bookings(room_id, hotel_id):
    if request.method == 'POST':
        #check if there exists history entites yet. 
        #is_there_history = History.query.all()
        #if not(is_there_history):
        #    print("No history found, a new batch was pushed to the DB!")
        #    populate_history()
        start_date = request.form.get('start_date') #booking start date. 
        end_date = request.form.get('end_date') #booking end date. 
        #print(start_date, end_date)
        is_valid_booking = validate_booking(room_id, hotel_id, start_date, end_date)
        is_valid_renting = validate_booking_with_rentings(room_id, hotel_id, start_date, end_date)
        if(is_valid_booking[0] and is_valid_renting[0] and not(user_is_employee())): #booking is valid. 
            hotel = Hotel.query.filter_by(hotel_ID = hotel_id).first()#find the  
            history = History.query.filter_by(hotel_ID = hotel_id).first() #find the history associated with the hotel. 
            booking_id = abs(int(current_user.id - int(time.time()))) #creating a unique booking id as a mix of user id and current time at creation of booking. 
            current_booking = Booking(booking_ID= booking_id, customer_ID=current_user.id, room_ID=room_id, hotel_ID=hotel_id, 
                                      hotel_chain_ID=hotel.hotel_chain_ID, 
                                      length_stay=int(is_valid_booking[1]), list_bookings=[],
                                      list_rentings=[],start_date=start_date, end_date=end_date)
            list_bookings = pickle.loads(history.list_bookings) 
            list_rentings = pickle.loads(history.list_rentings) 
            list_bookings.append(current_booking)
            history.list_bookings = pickle.dumps(list_bookings)
            #print(hotel.hotel_ID,list_bookings, list_rentings)
            db.session.add(history)
            db.session.commit()
            db.session.add(current_booking) #add user to database. 
            db.session.commit() #commit changes to server.
            
            flash('Your booking has been created!', 'success')
            customer_bookings = Booking.query.filter_by(customer_ID= current_user.id).all() 
            customer_rentings = Renting.query.filter_by(customer_ID= current_user.id).all()
            return render_template('profile.html', name = current_user.full_name, id = current_user.id, address = current_user.address, 
                                        DOR = current_user.DOR, bookings = customer_bookings, rentings = customer_rentings) 
        elif(user_is_employee()):
            flash('Cannot create booking as an employee.', 'error')
        #print(start_date, end_date)
        else:
            flash('Sorry! The dates selected are unavailable.', 'error')

    return render_template('booking.html', hotel_name = hotel_id)


