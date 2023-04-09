-- Create 'stores' table to store information about each store
CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    store_address VARCHAR(200),
    store_phone VARCHAR(20),
    store_email VARCHAR(100)
);

-- Create an index on store_name for faster searches by store name
CREATE INDEX idx_stores_store_name ON stores(store_name);

-- Create 'cameras' table to store information about each camera in the stores
CREATE TABLE cameras (
    camera_id INTEGER PRIMARY KEY,
    camera_name VARCHAR(100) NOT NULL,
    camera_model VARCHAR(100),
    store_id INTEGER NOT NULL,
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

-- Create an index on store_id for faster lookups of cameras by store
CREATE INDEX idx_cameras_store_id ON cameras(store_id);

-- Create 'points_of_service' table to store information about each point of service within the stores
CREATE TABLE points_of_service (
    pos_id INTEGER PRIMARY KEY,
    pos_name VARCHAR(100) NOT NULL,
    store_id INTEGER NOT NULL,
    camera_id INTEGER NOT NULL,
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id)
);

-- Create indexes on store_id and camera_id for faster lookups by store and camera
CREATE INDEX idx_points_of_service_store_id ON points_of_service(store_id);
CREATE INDEX idx_points_of_service_camera_id ON points_of_service(camera_id);

-- Create 'transactions' table to store information about each transaction
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    transaction_number VARCHAR(50) UNIQUE NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    pos_id INTEGER NOT NULL,
    thumbnail_url VARCHAR(200),
    footage_url VARCHAR(200),
    FOREIGN KEY (pos_id) REFERENCES points_of_service(pos_id)
);

-- Create an index on transaction_number and pos_id for faster lookups by transaction number and point of service
CREATE INDEX idx_transactions_transaction_number ON transactions(transaction_number);
CREATE INDEX idx_transactions_pos_id ON transactions(pos_id);

-- Create 'transaction_items' table to store information about each item sold in a transaction
CREATE TABLE transaction_items (
    id INTEGER PRIMARY KEY,
    transaction_id INTEGER NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    item_price FLOAT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

-- Create an index on transaction_id for faster lookups by transaction
CREATE INDEX idx_transaction_items_transaction_id ON transaction_items(transaction_id);

-- Create 'camera_events_uid' table to store camera event unique identifiers
CREATE TABLE camera_events_uid (
    event_type_uid VARCHAR(50) PRIMARY KEY,
    event_type_name VARCHAR(100) NOT NULL
);

-- Create a unique index on event_type_name for faster lookups by event type name
CREATE UNIQUE INDEX idx_camera_events_uid_event_type_name ON camera_events_uid(event_type_name);