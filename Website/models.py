from . import db
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
import pickle

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True) #PK #SIN
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    address = db.Column(db.String(255))
    DOR = db.Column(db.String(255)) #date of registration. 
    #RELATIONSHIP:
    bookings = db.relationship('Booking', back_populates = 'customer') #list of bookings associated with this user. 
    rentings = db.relationship('Renting', back_populates = 'customer') #list of rentings associated with this user. 

class Hotel_Chain(db.Model):
    __tablename__ = 'Hotel_Chain'
    hotel_chain_ID = db.Column(db.String(255), primary_key=True)
    address_COF = db.Column(db.String(255))
    num_hotels = db.Column(db.Integer)
    email = db.Column(db.String(255), unique=True)
    phone_num = db.Column(db.String(255), unique=True)
    hotels = db.relationship('Hotel', back_populates = 'parent_hotel_chain') #list of hotels belonging to this chain. 

class Hotel(db.Model):
    __tablename__ = 'Hotel'
    hotel_chain_ID = db.Column(db.String(255), db.ForeignKey('Hotel_Chain.hotel_chain_ID'))
    hotel_ID = db.Column(db.String(255), primary_key=True)
    address = db.Column(db.String(255))
    email = db.Column(db.String(255))
    rating = db.Column(db.Numeric(precision=2, scale=1))
    num_rooms = db.Column(db.Integer)
    manager = db.relationship('Employee', back_populates = "manages", uselist = False) # 1 to 1. One manager employee per hotel. 
    parent_hotel_chain = db.relationship('Hotel_Chain', back_populates = "hotels")
    rooms = db.relationship('Room', back_populates = "hotel") #list of rooms in the hotel. 
    history = db.relationship('History', back_populates = "hotel", uselist = True) #1 to 1. Every hotel has one history. 

class Employee(db.Model, UserMixin):
    __tablename__ = 'Employee'
    id = db.Column(db.Integer, primary_key=True) #PK #SIN
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(255))
    password = db.Column(db.String(255))
    DOR = db.Column(db.String(255)) #date of registration. 
    hotel_chain_ID = db.Column(db.String(255), db.ForeignKey('Hotel_Chain.hotel_chain_ID')) #FK
    hotel_ID = db.Column(db.String(255), db.ForeignKey('Hotel.hotel_ID')) #FK
    role = db.Column(db.String(255))
    manages = db.relationship("Hotel", back_populates="manager", uselist = False)

class Room(db.Model):
    __tablename__ = 'Room'
    hotel_chain_ID = db.Column(db.String(255), db.ForeignKey('Hotel_Chain.hotel_chain_ID')) #PK
    hotel_ID = db.Column(db.String(255), db.ForeignKey('Hotel.hotel_ID')) #FK
    room_ID = db.Column(db.Integer, primary_key=True) #FK
    room_number = db.Column(db.Integer)
    price = db.Column(db.Integer)
    amenities = db.Column(db.String(1000))
    capacity = db.Column(db.Integer)
    view = db.Column(db.String(255))
    is_extendable = db.Column(db.Boolean)
    damage_list = db.Column(db.String(500))
    room_status = db.Column(db.String(100))
    bookings = db.relationship('Booking', back_populates= "room") #list of associated bookings with this room. 
    rentings = db.relationship('Renting', back_populates= "room", uselist = True) #1 to 1. list of associated renting with this room. 
    hotel = db.relationship('Hotel', back_populates="rooms") #Every room should be associated with a hotel. 
    __table_args__ = (UniqueConstraint('hotel_ID', 'room_number', name='hotel_room_uc'),) #make sure that no rooms are created with the same number if they are in the same hotel!


class Renting(db.Model):
    __tablename__ = 'Renting'
    renting_ID = db.Column(db.Integer, primary_key=True)
    start_of_stay = db.Column(db.String(255)) #start of stay
    end_of_stay = db.Column(db.String(255)) #end of stay
    customer_ID = db.Column(db.Integer, db.ForeignKey('User.id'))
    hotel_chain_ID = db.Column(db.String(255), db.ForeignKey('Hotel_Chain.hotel_chain_ID'))
    hotel_ID = db.Column(db.String(255), db.ForeignKey('Hotel.hotel_ID'))
    room_ID = db.Column(db.Integer, db.ForeignKey('Room.room_ID'))
    list_bookings = db.Column(db.PickleType)
    list_rentings = db.Column(db.PickleType)
    room = db.relationship("Room", back_populates="rentings") #1 to 1. Every renting must be associated with a room.
    customer = db.relationship("User", back_populates="rentings") #Every booking should belong to a customer.

class Booking(db.Model):
    __tablename__ = 'Booking'
    booking_ID = db.Column(db.Integer, primary_key=True)
    customer_ID = db.Column(db.Integer, db.ForeignKey('User.id'))
    room_ID = db.Column(db.Integer, db.ForeignKey('Room.room_ID'))
    hotel_ID = db.Column(db.String(255), db.ForeignKey('Hotel.hotel_ID'))
    hotel_chain_ID = db.Column(db.String(255), db.ForeignKey('Hotel_Chain.hotel_chain_ID'))
    length_stay = db.Column(db.Integer) #number of days. 
    list_bookings = db.Column(db.PickleType)
    list_rentings  = db.Column(db.PickleType)
    start_date = db.Column(db.String(255))
    end_date = db.Column(db.String(255))
    room = db.relationship("Room", back_populates="bookings") #1 to 1. Every bookin must refer to one room. 
    customer = db.relationship("User", back_populates="bookings") #Every booking should belong to a customer. 

class History(db.Model):
    __tablename__ = 'History'
    hotel_ID = db.Column(db.String(255), db.ForeignKey('Hotel.hotel_ID'), primary_key=True)
    hotel_chain_ID = db.Column(db.String(255), db.ForeignKey('Hotel_Chain.hotel_chain_ID'), primary_key=True)
    list_rentings = db.Column(db.PickleType)
    list_bookings = db.Column(db.PickleType)
    hotel = db.relationship('Hotel', back_populates= "history", uselist= True) #1 to 1. A history can ony be associated to one hotel. 


#creating table view... 1
class ViewAvailableRoomsPerAreaView(Base):
    __tablename__ = 'ViewAvailableRoomsPerAreaView' 
    __table_args__ = {'info': dict(is_view=True)}
    #__abstract__ = True
    # Define primary key and any other necessary columns, 
    # if autoload is not used or not working as expected
    location = db.Column(db.String(255), primary_key=True)
    available_rooms = db.Column(db.Integer)


#creating table view... 2
class ViewHotelTotalCapacityView(Base):
    __tablename__ = 'ViewhoteltotalcapacityView'  
    __table_args__ = {'info': dict(is_view=True)}
   # __abstract__ = True
    # Define primary key and any other necessary columns, 
    # if autoload is not used or not working as expected
    hotel_ID = db.Column(db.String(255), primary_key=True)
    total_capacity = db.Column(db.Integer)
