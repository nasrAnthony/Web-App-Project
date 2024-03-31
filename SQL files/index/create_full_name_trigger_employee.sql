DELIMITER $$

CREATE TRIGGER CheckEmployeeNameBeforeInsert
BEFORE INSERT ON employee
FOR EACH ROW
BEGIN
   IF CHAR_LENGTH(NEW.full_name) < 3 THEN
     SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Minimum Employee full name must be at least 3 characters.';
   END IF;
END$$

DELIMITER ;
