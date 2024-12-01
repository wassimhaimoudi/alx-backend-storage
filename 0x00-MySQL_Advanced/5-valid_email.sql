-- A SQL script that creates a trigger that resets the attribute valid_email only when email
-- has been changed

DELIMITER $$
CREATE TRIGGER after_email_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
	IF OLD.email <> NEW.email THEN
		SET NEW.valid_email = 0;
	END IF;
END$$
DELIMITER ;
