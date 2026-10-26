CREATE DATABASE IF NOT EXISTS rechannel_crm;
USE rechannel_crm;

-- Users Table with permanent credentials
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

INSERT INTO users (username, password) VALUES 
('rcfpavika', 'rcfpavika'),
('rcfaarya', 'rcfaarya');

-- Appointments Table
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    appointment_date DATE,
    appointment_time TIME,
    order_manager VARCHAR(100),
    reference VARCHAR(100)
);

-- Bookings Table (with exact requested outfit checkboxes)
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    booking_date DATE,
    trial_date DATE,
    order_manager VARCHAR(100),
    sw TINYINT DEFAULT 0,
    nw TINYINT DEFAULT 0,
    jp TINYINT DEFAULT 0,
    bomber TINYINT DEFAULT 0,
    suit TINYINT DEFAULT 0,
    bundi TINYINT DEFAULT 0,
    iw TINYINT DEFAULT 0,
    kurta TINYINT DEFAULT 0
);

-- Trials Table
CREATE TABLE IF NOT EXISTS trials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    trial_date DATE,
    first_trial_done TINYINT DEFAULT 0,
    second_trial_done TINYINT DEFAULT 0,
    delivery_done TINYINT DEFAULT 0
);