-- 002_seed.sql: demo data. Demo login: demo@example.com / demo1234 (Argon2id hash below)
INSERT INTO users (email, password_hash) VALUES
  ('demo@example.com', '$argon2id$v=19$m=65536,t=3,p=4$aPK+t0Ox6rSKYN5ZTXFuJA$3tw/x/gsxsQY8kZ30jz5zfiwqIwPsvwdFmrlHxxDNf0');

INSERT INTO products (sku, name, description, price_cents, stock) VALUES
  ('MUG-001',  'Ceramic Mug',        'Stoneware mug, 350 ml.',               1200, 50),
  ('TEE-001',  'Cotton T-Shirt',     'Organic cotton, unisex fit.',          2500, 40),
  ('BAG-001',  'Canvas Tote Bag',    'Heavy canvas with inner pocket.',      1800, 30),
  ('NOTE-001', 'Dot Grid Notebook',  'A5, 160 pages, lay-flat binding.',      900, 100),
  ('PEN-001',  'Gel Pen Set',        'Five colours, 0.5 mm.',                 650, 80),
  ('LAMP-001', 'Desk Lamp',          'LED, three brightness levels.',        4500, 12),
  ('HEAD-001', 'Wired Headphones',   'Closed-back, 1.2 m cable.',            3900, 20),
  ('WATCH-01', 'Minimal Wall Clock', 'Silent movement, 30 cm. Low stock.',   3200, 3);
