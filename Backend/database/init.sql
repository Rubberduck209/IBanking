SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS user_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE user_DB;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    phone_number VARCHAR(30),
    email VARCHAR(255),
    available_balance DECIMAL(15, 2) DEFAULT 0.00,
    version INT DEFAULT 1
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


INSERT INTO users (username, password_hash, full_name, phone_number, email, available_balance, version)
VALUES 
('nguyenvana', '$2b$12$fZIYCAidyvqeAqjhWDRg9.eS2DSqDaiSyW/JL7oSIcFls4LJJ7gxq', 'Nguyễn Văn A', '0901234567', 'chungocanh1901@gmail.com', 5000000000.00, 1),
('lethib', '$2a$12$E8zJ6G5w0eN0pPXU31.J7s8Qo0Z6m1e9n5p3xV6X7Y9z2A1bD', 'Lê Thị B', '0987654321', 'lethib@gmail.com', 12500000.50, 1),
('tranvanc', '$2a$12$T2yJ6G5w0eN0pPXU31.J7s8Qo0Z6m1e9n5p3xV6X7Y9z2A1bE', 'Trần Văn C', '0912345678', 'tranvanc@yahoo.com', 150000.00, 1),
('hoangthid', '$2a$12$H4xJ6G5w0eN0pPXU31.J7s8Qo0Z6m1e9n5p3xV6X7Y9z2A1bF', 'Hoàng Thị D', '0934567890', 'hoangthid@outlook.com', 0.00, 1),
('vuongvane', '$2a$12$V5wJ6G5w0eN0pPXU31.J7s8Qo0Z6m1e9n5p3xV6X7Y9z2A1bG', 'Vương Văn E', '0978123456', 'vuongvane@gmail.com', 7500000.00, 1);




CREATE DATABASE IF NOT EXISTS tuition_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tuition_DB;

CREATE TABLE tuitions (
    student_id VARCHAR(255) PRIMARY KEY,
    student_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    tuition_fee_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    amount_due DECIMAL(15, 2),
    status_ VARCHAR(50),
    version INT DEFAULT 1
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO tuitions (student_id, student_name, tuition_fee_name, amount_due, status_) VALUES
('TDTU24001', 'Nguyễn Văn A', 'Học phí HK1 Năm học 2026-2027', 15500000.00, 'Chưa thanh toán'),
('TDTU24002', 'Lê Thị B', 'Học phí HK1 Năm học 2026-2027', 15500000.00, 'Đã thanh toán'),
('TDTU24003', 'Trần Thị Bảo', 'Học phí Giáo dục Quốc phòng', 3200000.00, 'Chưa thanh toán'),
('TDTU24004', 'Lê Hoàng Cường', 'Học phí Tiếng Anh Tăng cường', 8500000.00, 'Chưa thanh toán'),
('TDTU24005', 'Phạm Minh Duy', 'Học phí HK2 Năm học 2025-2026', 14000000.00, 'Đã thanh toán');


CREATE DATABASE IF NOT EXISTS payment_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payment_DB;

CREATE TABLE `transactions` (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id INT,
    student_id VARCHAR(255),
    amount DECIMAL(15, 2),
    status_ VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE otp_codes (
    otp_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id VARCHAR(255),
    code_ VARCHAR(255),
    expires_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (transaction_id) REFERENCES `transactions`(transaction_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;