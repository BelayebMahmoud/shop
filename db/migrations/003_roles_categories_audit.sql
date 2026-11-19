-- 003_roles_categories_audit.sql: roles (FR-02), categories (FR-03), order workflow and discount (FR-08, BR-04),
-- case-insensitive uniqueness (BR-07, Q-06), immutable audit log (FR-11), one seeded user per role.

-- ---------------------------------------------------------------- users: role and active flag
ALTER TABLE users
  ADD COLUMN role      TEXT    NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER', 'STAFF', 'ADMIN')),
  ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
CREATE UNIQUE INDEX uq_users_email_lower ON users (lower(email));

-- Seed logins (development only): admin@example.com / admin1234, staff@example.com / staff1234 (Argon2id).
-- demo@example.com / demo1234 from 002 stays CUSTOMER.
INSERT INTO users (email, password_hash, role) VALUES
  ('admin@example.com', '$argon2id$v=19$m=65536,t=3,p=4$z1Dgwcw6eM6mQ6XIgQ08yQ$+2sQEUEqXwQsli2K5yxwrF/dwJ8KaSeIhuM3enI+muk', 'ADMIN'),
  ('staff@example.com', '$argon2id$v=19$m=65536,t=3,p=4$kP54bLK+Ujg/U34ctGBbnw$UijCII+3+ikFQoeI5uivCxWKFsa/2smFWd8svLvi5JU', 'STAFF');

-- ---------------------------------------------------------------- categories (1-N products)
CREATE TABLE categories (
  id         BIGSERIAL   PRIMARY KEY,
  name       TEXT        NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_categories_name_lower ON categories (lower(name));

INSERT INTO categories (name) VALUES ('Cuisine'), ('Vêtements'), ('Bagagerie'), ('Papeterie'), ('Maison'), ('Audio');

ALTER TABLE products ADD COLUMN category_id BIGINT REFERENCES categories(id);
UPDATE products p SET category_id = c.id
FROM (VALUES ('MUG-001', 'Cuisine'), ('TEE-001', 'Vêtements'), ('BAG-001', 'Bagagerie'), ('NOTE-001', 'Papeterie'),
             ('PEN-001', 'Papeterie'), ('LAMP-001', 'Maison'), ('HEAD-001', 'Audio'), ('WATCH-01', 'Maison'))
     AS m(sku, category) JOIN categories c ON c.name = m.category
WHERE p.sku = m.sku;
UPDATE products SET category_id = (SELECT id FROM categories WHERE name = 'Maison') WHERE category_id IS NULL;
ALTER TABLE products ALTER COLUMN category_id SET NOT NULL;
CREATE INDEX idx_products_category ON products (category_id);
CREATE INDEX idx_products_price ON products (price_cents);
CREATE UNIQUE INDEX uq_products_sku_lower ON products (lower(sku));

-- ---------------------------------------------------------------- orders: workflow statuses and discount
ALTER TABLE orders DROP CONSTRAINT orders_status_check;
ALTER TABLE orders ADD CONSTRAINT orders_status_check
  CHECK (status IN ('PLACED', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED'));
ALTER TABLE orders
  ADD COLUMN subtotal_cents INTEGER     NOT NULL DEFAULT 0 CHECK (subtotal_cents >= 0),
  ADD COLUMN discount_cents INTEGER     NOT NULL DEFAULT 0 CHECK (discount_cents >= 0),
  ADD COLUMN updated_at     TIMESTAMPTZ NOT NULL DEFAULT now();
UPDATE orders SET subtotal_cents = total_cents;
ALTER TABLE orders ADD CONSTRAINT orders_total_consistent CHECK (total_cents = subtotal_cents - discount_cents);
CREATE INDEX idx_orders_created_at ON orders (created_at);
CREATE INDEX idx_order_items_product ON order_items (product_id);

-- ---------------------------------------------------------------- audit log (append-only)
CREATE TABLE audit_log (
  id         BIGSERIAL   PRIMARY KEY,
  actor_id   BIGINT      REFERENCES users(id),
  action     TEXT        NOT NULL,
  entity     TEXT        NOT NULL,
  entity_id  BIGINT,
  details    JSONB       NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_log_created_at ON audit_log (created_at);

-- Defence in depth for FR-11: even a direct SQL UPDATE or DELETE is refused.
CREATE FUNCTION audit_log_is_append_only() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'audit_log is append-only (FR-11)';
END;
$$;
CREATE TRIGGER audit_log_no_update_delete
  BEFORE UPDATE OR DELETE ON audit_log
  FOR EACH ROW EXECUTE FUNCTION audit_log_is_append_only();
