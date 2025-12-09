ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('');
ALTER USER 'root'@'127.0.0.1' IDENTIFIED VIA mysql_native_password USING PASSWORD('');
FLUSH PRIVILEGES;

DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;
USE testdb;

CREATE USER IF NOT EXISTS 'appuser'@'127.0.0.1' IDENTIFIED BY 'app_pass123';
CREATE USER IF NOT EXISTS 'appuser'@'localhost' IDENTIFIED BY 'app_pass123';
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'app_pass123';
GRANT ALL PRIVILEGES ON testdb.* TO 'appuser'@'127.0.0.1';
GRANT ALL PRIVILEGES ON testdb.* TO 'appuser'@'localhost';
GRANT ALL PRIVILEGES ON testdb.* TO 'appuser'@'%';
FLUSH PRIVILEGES;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    signup_date DATE
);

CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_name VARCHAR(100),
    sale_amount DECIMAL(10,2),
    sale_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

INSERT INTO customers (customer_name, email, city, signup_date) VALUES
('John Doe', 'john@email.com', 'New York', '2023-01-15'),
('Jane Smith', 'jane@email.com', 'Los Angeles', '2023-02-20'),
('Bob Johnson', 'bob@email.com', 'Chicago', '2023-03-10'),
('Alice Brown', 'alice@email.com', 'Houston', '2023-04-05'),
('Charlie Wilson', 'charlie@email.com', 'Phoenix', '2023-05-12');

INSERT INTO sales (customer_id, product_name, sale_amount, sale_date) VALUES
(1, 'Laptop', 1200.00, '2023-06-01'),
(1, 'Mouse', 25.00, '2023-06-02'),
(2, 'Monitor', 300.00, '2023-06-03'),
(3, 'Keyboard', 80.00, '2023-06-04'),
(2, 'Webcam', 150.00, '2023-06-05'),
(4, 'Laptop', 1200.00, '2023-06-06'),
(5, 'Tablet', 400.00, '2023-06-07'),
(1, 'Headphones', 200.00, '2023-06-08');
