CREATE TABLE accounts (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(16) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    password CHAR(60) NOT NULL
);
