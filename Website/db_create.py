#quick script to create database.
import mysql.connector
db = mysql.connector.connect(
    host = "localhost", 
    user = "tony", 
    password = "Aliame123", 
)

cursor = db.cursor()
#cursor.execute("CREATE DATABASE eHotelsDB") #DONT UNCOMMENT THIS LINE, WILL CREATE DB AGAIN, MAY WIPE DATA. 

cursor.execute("SHOW DATABASES")
for database in cursor:
    print(database)