-- 001_schema.sql: applied once by Postgres on first start (docker-entrypoint-initdb.d)
CREATE TABLE users (
  id            BIGSERIAL PRIMARY KEY,
  email         TEXT        NOT NULL UNIQUE,
  password_hash TEXT        NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products (
  id          BIGSERIAL PRIMARY KEY,
  sku         TEXT        NOT NULL UNIQUE,
  name        TEXT        NOT NULL,
  description TEXT        NOT NULL DEFAULT '',
  price_cents INTEGER     NOT NULL CHECK (price_cents >= 0),
  stock       INTEGER     NOT NULL CHECK (stock >= 0),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT      NOT NULL REFERENCES users(id),
  status      TEXT        NOT NULL DEFAULT 'PLACED' CHECK (status IN ('PLACED', 'PAID', 'CANCELLED')),
  total_cents INTEGER     NOT NULL CHECK (total_cents >= 0),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
  order_id         BIGINT  NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id       BIGINT  NOT NULL REFERENCES products(id),
  quantity         INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
  PRIMARY KEY (order_id, product_id)
);

CREATE INDEX idx_orders_user_id    ON orders (user_id);
CREATE INDEX idx_products_name_low ON products (lower(name));
