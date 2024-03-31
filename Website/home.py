from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from . import db
from .models import Hotel, Hotel_Chain, Room, Booking, Renting, History, AvailableRoomsPerArea
from datetime import datetime
from collections import namedtuple
import time, pickle

home_page = Blueprint('home_page', __name__)

@home_page.route("/", methods=['GET', 'POST'])#decorator
@login_required
def home():
    #fetch top rated hotels. fetch all with rating greater than 8.5 
    top_rated_hotels = Hotel.query.filter(Hotel.rating > 8.5).all()
   # print(top_rated_hotels)
    rooms_per_area_view = AvailableRoomsPerArea.query.all()
    #available_rooms_list = [
    #    {'location': area.location, 'available_rooms': area.available_rooms}
    #    for area in rooms_per_area_view
    #]
    return render_template('home.html', hotels = top_rated_hotels, available_rooms= rooms_per_area_view )
    #return render_template('home.html', hotels = top_rated_hotels, available_rooms= available_rooms_list )