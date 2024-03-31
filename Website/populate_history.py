from . import db
from .models import Hotel,History
import pickle

#will populate the history for each of the existing hotels as empty pickle lists []. 
#only need to run this script once. 

def populate_history():
    hotels = Hotel.query.all()
    for hotel in hotels:
        list_rentings = pickle.dumps([])
        list_bookings = pickle.dumps([])
        new_history = History(hotel_ID=str(hotel.hotel_ID), hotel_chain_ID=str(hotel.hotel_chain_ID), 
                      list_rentings=list_rentings, list_bookings=list_bookings)
        db.session.add(new_history)
        db.session.commit()


#call function to populate
populate_history()