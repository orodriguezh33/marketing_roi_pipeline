-- Esquema de las 9 tablas del dataset Olist (Brazilian E-Commerce Public Dataset,
-- Kaggle: olistbr/brazilian-ecommerce). Nombres de columnas calcados de los CSV
-- originales -- incluye typos del dataset real (product_name_lenght,
-- product_description_lenght) para que infra/postgres/seed_olist.py pueda cargar
-- cada CSV sin tener que renombrar columnas.
--
-- Sin FKs: la integridad referencial se valida en dbt (`relationships` tests,
-- Fase 4), no acá -- esto es la capa fuente/CDC, no un modelo curado.
-- order_reviews no tiene PK: el dataset real trae review_id duplicado en ~100
-- filas; deduplicar es responsabilidad de dbt staging (Fase 3), no de esta capa.

CREATE TABLE product_category_name_translation (
    product_category_name          text PRIMARY KEY,
    product_category_name_english  text NOT NULL
);

CREATE TABLE customers (
    customer_id               text PRIMARY KEY,
    customer_unique_id        text NOT NULL,
    customer_zip_code_prefix  integer,
    customer_city             text,
    customer_state            text
);
CREATE INDEX idx_customers_unique_id ON customers (customer_unique_id);

CREATE TABLE sellers (
    seller_id               text PRIMARY KEY,
    seller_zip_code_prefix  integer,
    seller_city             text,
    seller_state            text
);

CREATE TABLE products (
    product_id                     text PRIMARY KEY,
    product_category_name          text,
    product_name_lenght            integer,
    product_description_lenght     integer,
    product_photos_qty             integer,
    product_weight_g               integer,
    product_length_cm              integer,
    product_height_cm              integer,
    product_width_cm               integer
);
CREATE INDEX idx_products_category ON products (product_category_name);

CREATE TABLE geolocation (
    geolocation_zip_code_prefix  integer,
    geolocation_lat              double precision,
    geolocation_lng              double precision,
    geolocation_city             text,
    geolocation_state            text
);
CREATE INDEX idx_geolocation_zip ON geolocation (geolocation_zip_code_prefix);
ALTER TABLE geolocation REPLICA IDENTITY FULL;

CREATE TABLE orders (
    order_id                        text PRIMARY KEY,
    customer_id                     text NOT NULL,
    order_status                    text NOT NULL,
    order_purchase_timestamp        timestamp NOT NULL,
    order_approved_at               timestamp,
    order_delivered_carrier_date    timestamp,
    order_delivered_customer_date   timestamp,
    order_estimated_delivery_date   timestamp NOT NULL
);
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_purchase_timestamp ON orders (order_purchase_timestamp);

CREATE TABLE order_items (
    order_id             text NOT NULL,
    order_item_id        smallint NOT NULL,
    product_id           text NOT NULL,
    seller_id            text NOT NULL,
    shipping_limit_date  timestamp NOT NULL,
    price                numeric(10, 2) NOT NULL,
    freight_value        numeric(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);
CREATE INDEX idx_order_items_seller_id ON order_items (seller_id);

CREATE TABLE order_payments (
    order_id              text NOT NULL,
    payment_sequential    smallint NOT NULL,
    payment_type          text NOT NULL,
    payment_installments  smallint NOT NULL,
    payment_value         numeric(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE order_reviews (
    review_id                 text NOT NULL,
    order_id                  text NOT NULL,
    review_score              smallint NOT NULL,
    review_comment_title      text,
    review_comment_message    text,
    review_creation_date      timestamp NOT NULL,
    review_answer_timestamp   timestamp NOT NULL
);
CREATE INDEX idx_order_reviews_order_id ON order_reviews (order_id);
CREATE INDEX idx_order_reviews_review_id ON order_reviews (review_id);
ALTER TABLE order_reviews REPLICA IDENTITY FULL;
