DELIMITER $$

CREATE TRIGGER CheckIDLengthBeforeInsertEmployee
BEFORE INSERT ON employee
FOR EACH ROW
BEGIN
   IF CHAR_LENGTH(NEW.id) < 5 THEN
     SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Minimum characters in ID field is 5.';
   END IF;
END$$

DELIMITER ;
