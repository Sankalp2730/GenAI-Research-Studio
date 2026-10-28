-- Sample database for the Text-to-SQL module
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
);

INSERT INTO products (product_name, category, price, stock) VALUES
('Laptop', 'Electronics', 55000, 12),
('Headphones', 'Electronics', 2500, 35),
('Office Chair', 'Furniture', 6500, 8),
('Notebook', 'Stationery', 80, 150);
