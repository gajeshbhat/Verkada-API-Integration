CREATE USER 'jdsports_user'@'%' IDENTIFIED WITH mysql_native_password BY '';
GRANT ALL PRIVILEGES ON jdsports.* TO 'jdsports_user'@'%';
SET PASSWORD FOR 'jdsports_user'@'%' = 'jdsports_password';
