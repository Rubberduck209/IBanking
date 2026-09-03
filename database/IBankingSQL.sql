
CREATE DATABASE user_DB;
USE user_DB;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    full_name VARCHAR(255),
    phone_number VARCHAR(30),
    email VARCHAR(255),
    available_balance DECIMAL(15, 2) DEFAULT 0.00, 
    version INT DEFAULT 1 
);


CREATE DATABASE tuition_DB;
USE tuition_DB;

CREATE TABLE tuitions (
    student_id VARCHAR(255) PRIMARY KEY,
    student_name VARCHAR(255),
    tuition_fee_name VARCHAR(255),
    amount_due DECIMAL(15, 2), 
    status_ VARCHAR(50),
    version INT DEFAULT 1
);


CREATE DATABASE payment_DB;
USE payment_DB;


CREATE TABLE `transactions` (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id INT,
    student_id VARCHAR(255),
    amount DECIMAL(15, 2), 
    status_ VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE otp_codes (
    otp_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id VARCHAR(255),
    code_ VARCHAR(255),
    expires_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (transaction_id) REFERENCES `transactions`(transaction_id)
);