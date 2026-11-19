-- 004_volume_seed.sql: 50,000 deterministic products for FR-10 / QR-PE-02, and a trigram index for text search.
-- Loaded by Postgres on first start. The default pytest database skips this file (controlled data, see
-- backend/tests/api/conftest.py); volume and performance tests load it explicitly.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

INSERT INTO products (sku, name, description, price_cents, stock, category_id)
SELECT
  'GEN-' || lpad(n::text, 6, '0'),
  (ARRAY['Mug', 'Tote', 'Notebook', 'Lamp', 'Headphones', 'Clock', 'Pen', 'Shirt', 'Bowl', 'Speaker'])[1 + n % 10]
    || ' ' || (ARRAY['Classic', 'Mini', 'Pro', 'Eco', 'Deluxe', 'Travel', 'Studio', 'Urban'])[1 + (n / 10) % 8]
    || ' ' || n,
  'Generated catalogue item ' || n || '.',
  100 + (n * 7919) % 25000,              -- 1.00 to 250.99 EUR, spread over the whole range
  (n * 13) % 60,                         -- 0 to 59: some out of stock, some below 5
  (SELECT id FROM categories ORDER BY id OFFSET (n % 6) LIMIT 1)
FROM generate_series(1, 50000) AS n;

CREATE INDEX idx_products_name_trgm ON products USING gin (lower(name) gin_trgm_ops);
ANALYZE products;
