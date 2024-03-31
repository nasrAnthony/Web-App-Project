DELIMITER $$

CREATE TRIGGER CheckUserNameLengthBeforeInsert
BEFORE INSERT ON user
FOR EACH ROW
BEGIN
   IF CHAR_LENGTH(NEW.full_name) < 3 THEN
     SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Minimum User full name must be at least 3 characters.';
   END IF;
END$$

DELIMITER ;
