CREATE TABLE users (
  uid SERIAL NOT NULL,
  username VARCHAR,
  first_name VARCHAR,
  last_name VARCHAR,
  password VARCHAR,
  email VARCHAR,
  PRIMARY KEY (uid)
);

CREATE TYPE product_status AS ENUM ('available', 'pending', 'sold');

CREATE TABLE products(
  product_id SERIAL NOT NULL,
  name VARCHAR,
  product_number INT,
  status product_status,
  PRIMARY KEY (product_id)
);

CREATE TYPE order_status AS ENUM ('placed', 'approved', 'delivered');

CREATE TABLE orders(
  order_id SERIAL NOT NULL,
  status order_status,
  PRIMARY KEY (order_id)
);

CREATE TABLE users_orders(
  uid INTEGER,
  order_id INTEGER,
  FOREIGN KEY (uid) REFERENCES users(uid),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE order_products(
  order_id INTEGER,
  product_id INTEGER,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);
