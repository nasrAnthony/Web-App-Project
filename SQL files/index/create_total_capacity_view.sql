CREATE VIEW HotelTotalCapacity AS
SELECT h.hotel_ID, SUM(r.capacity) AS total_capacity
FROM hotel AS h
JOIN room AS r ON h.hotel_ID = r.hotel_ID
GROUP BY h.hotel_ID;