CREATE VIEW AvailableRoomsPerArea AS
SELECT 
	TRIM(SUBSTRING_INDEX(h.address, ',', -1)) AS location, -- get city/country part after comma
    COUNT(r.room_id) AS available_rooms
FROM hotel AS h
JOIN room AS r ON h.hotel_ID = r.hotel_ID
WHERE r.room_status = 'available'
GROUP BY location;