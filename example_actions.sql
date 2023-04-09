-- Insert a new store into the 'stores' table
INSERT INTO stores (store_id, store_name, store_address, store_phone, store_email) 
VALUES (3, 'JD Sports Manchester', '1 Arndale Centre, Manchester M4 2HU', '0161 831 7320', 'manchester@jdsports.co.uk');

-- Insert a new camera into the 'cameras' table
INSERT INTO cameras (camera_id, camera_name, camera_model, store_id) 
VALUES (6, 'Camera 1', 'Verkada D30', 3);

-- Insert a new point of service into the 'points_of_service' table
INSERT INTO points_of_service (pos_id, pos_name, store_id, camera_id) 
VALUES (6, 'Checkout 1', 3, 6);

-- Insert a new transaction into the 'transactions' table
INSERT INTO transactions (transaction_id, transaction_number, transaction_date, pos_id, thumbnail_url, footage_url) 
VALUES (3, '12345', '2023-04-01 09:00:00', 6, 'http://example.com/thumbnails/3.jpg', 'http://example.com/footage/3.mp4');

-- Insert a new transaction item into the 'transaction_items' table
INSERT INTO transaction_items (id, transaction_id, item_name, item_price) 
VALUES (5, 3, 'Nike Air Max', 79.99);

-- Select all transactions for a specific store
SELECT transactions.*, stores.store_name, transaction_items.item_name, transaction_items.item_price 
FROM transactions 
JOIN points_of_service ON transactions.pos_id = points_of_service.pos_id 
JOIN cameras ON points_of_service.camera_id = cameras.camera_id 
JOIN stores ON points_of_service.store_id = stores.store_id 
JOIN transaction_items ON transactions.transaction_id = transaction_items.transaction_id 
WHERE stores.store_id = 3;

-- Select the total sales for a specific store
SELECT SUM(transaction_items.item_price) AS total_sales 
FROM transaction_items 
JOIN transactions ON transaction_items.transaction_id = transactions.transaction_id 
JOIN points_of_service ON transactions.pos_id = points_of_service.pos_id 
WHERE points_of_service.store_id = 3;

-- Retrieve all stores in the database
SELECT * FROM stores;

-- Retrieve all transactions in the database with their associated item names and prices
SELECT transactions.*, transaction_items.item_name, transaction_items.item_price
FROM transactions
JOIN transaction_items ON transactions.transaction_id = transaction_items.transaction_id;

-- Retrieve the total sales for a specific store:
SELECT SUM(transaction_items.item_price) AS total_sales
FROM transactions
JOIN transaction_items ON transactions.transaction_id = transaction_items.transaction_id
JOIN points_of_service ON transactions.pos_id = points_of_service.pos_id
WHERE points_of_service.store_id = <store_id>;

-- Retrieve the total sales for each store in the database:
SELECT stores.store_name, SUM(transaction_items.item_price) AS total_sales
FROM transactions
JOIN transaction_items ON transactions.transaction_id = transaction_items.transaction_id
JOIN points_of_service ON transactions.pos_id = points_of_service.pos_id
JOIN stores ON points_of_service.store_id = stores.store_id
GROUP BY stores.store_name;

-- Retrieve the names of all stores that have at least one camera:
SELECT DISTINCT stores.store_name
FROM stores
JOIN cameras ON stores.store_id = cameras.store_id;

-- Insert a new event type into the 'camera_events_uid' table
INSERT INTO camera_events_uid (event_type_uid, event_type_name)
VALUES ('EVT006', 'Warehouse Loading');
