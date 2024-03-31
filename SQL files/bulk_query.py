#this script will generate all 200 ueries needed to populate the room table within the db. 
import random
'''
here are some example queries. 
INSERT INTO `ehotelsdb`.`room` (`hotel_chain_ID`, `hotel_ID`, `room_ID`, `room_number`, `price`, `amenities`, `capacity`, `view`, `is_extendable`, `damage_list`, `room_status`) VALUES ('Stone Hotels', 'Brownside Central Hotel', '1', '2', '200', 'full', '4', 'Sea', '1', 'none', 'available');
INSERT INTO `ehotelsdb`.`room` (`hotel_chain_ID`, `hotel_ID`, `room_ID`, `room_number`, `price`, `amenities`, `capacity`, `view`, `is_extendable`, `damage_list`, `room_status`) VALUES ('Stone Hotels', 'Brownside Central Hotel', '2', '4', '150', 'full', '3', 'Mountain', '1', 'none', 'available');
INSERT INTO `ehotelsdb`.`room` (`hotel_chain_ID`, `hotel_ID`, `room_ID`, `room_number`, `price`, `amenities`, `capacity`, `view`, `is_extendable`, `damage_list`, `room_status`) VALUES ('Stone Hotels', 'Brownside Central Hotel', '3', '5', '125', 'full', '2', 'Mountain', '1', 'none', 'available');
INSERT INTO `ehotelsdb`.`room` (`hotel_chain_ID`, `hotel_ID`, `room_ID`, `room_number`, `price`, `amenities`, `capacity`, `view`, `is_extendable`, `damage_list`, `room_status`) VALUES ('Stone Hotels', 'Brownside Central Hotel', '4', '10','250', 'full', '5', 'Mountain', '1', 'none', 'available');
INSERT INTO `ehotelsdb`.`room` (`hotel_chain_ID`, `hotel_ID`, `room_ID`, `room_number`, `price`, `amenities`, `capacity`, `view`, `is_extendable`, `damage_list`, `room_status`) VALUES ('Stone Hotels', 'Brownside Central Hotel', '5', '8', '400', 'full', '7', 'Sea', '1', 'none', 'available');

'''

out_file = open('create_rooms.sql', 'w')
all_hotels_file = open('create_hotels.sql', 'r')

def populate_hotel_list(hotel_file): #finds all the hotels in SQL file.
    hotels_found = []  
    for line in hotel_file.readlines():
        tmp = line.split('VALUES')
        #tmp2 = tmp[1].split(',')[1].split('(')[1]\
        tmp2 = tmp[1].split(',')[1]
        tmp3 = tmp[1].split(',')[0].split('(')[1]
        hotels_found.append((tmp2, tmp3))
    return hotels_found
    

base_query = "INSERT INTO `ehotelsdb`.`room` (`hotel_chain_ID`, `hotel_ID`, `room_ID`, `room_number`, `price`, `amenities`, `capacity`, `view`, `is_extendable`, `damage_list`, `room_status`) VALUES ("

#hotel_chain_list = ['TNC Hotels', 'The Barriot', 'Monak Inn', 'Phab Hotel', 'Stone Hotels' ] #all hotel chains. 

hotel_list = populate_hotel_list(all_hotels_file)
count_ID = 1
for hotel in hotel_list:
    flag = False #set true once 5 rooms are created
    count = 1
    while count <6:
        view_flip = random.randint(0,1) #1 -> sea, 0 -> mountain
        if(view_flip == 0):
            view = 'Mountain'
        elif(view_flip == 1):
            view = 'Sea'
        is_extendable_flip = random.randint(0,1) #1 -> extendable, 0 -> not extendable
        query = base_query + f"{hotel[1]}"+", "+f"{hotel[0]}"+", '"+f"{count_ID}"+"', '"+f"{count_ID}"+"', '"+f"{random.randint(30,500)}"+"', "+"'full'"+", '"+f"{random.randint(1,10)}"+"', '"+f'{view}'+"', '"+f'{is_extendable_flip}'+"', "+"'none'"+", "+"'available');"+'\n'
        out_file.write(query)
        count_ID +=1
        count+=1



