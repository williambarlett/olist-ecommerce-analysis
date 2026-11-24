-- 03_clean_views.sql
-- Builds "clean" views on top of the raw tables.
-- A view is a saved query: it stores no data of its own, it just re-runs
-- the SELECT whenever you query it. The raw tables stay untouched.

-- ------------------------------------------------------------------
-- 1. orders_clean: one row per delivered order, Jan 2017 - Aug 2018
-- ------------------------------------------------------------------
DROP VIEW IF EXISTS orders_clean;   -- lets you re-run this file safely

CREATE VIEW orders_clean AS
SELECT
    o.order_id,
    c.customer_unique_id,                -- the real person (for repeat purchases)
    c.customer_state,

    -- Dates are stored as text; datetime() makes sure they're in a
    -- standard 'YYYY-MM-DD HH:MM:SS' format SQLite can do math on.
    datetime(o.order_purchase_timestamp)      AS purchased_at,
    strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,
    datetime(o.order_delivered_customer_date) AS delivered_at,
    datetime(o.order_estimated_delivery_date) AS estimated_at,

    -- julianday() turns a date into a number of days, so subtracting two
    -- of them gives the gap in days (with decimals for hours).
    ROUND(julianday(o.order_delivered_customer_date)
        - julianday(o.order_purchase_timestamp), 1)      AS delivery_days,
    ROUND(julianday(o.order_delivered_customer_date)
        - julianday(o.order_estimated_delivery_date), 1) AS days_late,

    -- 1 = arrived after the promised date, 0 = on time or early,
    -- NULL = no delivery date recorded (can't tell).
    -- Compare calendar dates only: the estimate has no time of day,
    -- so arriving on the estimated day counts as on time.
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        WHEN date(o.order_delivered_customer_date)
           > date(o.order_estimated_delivery_date) THEN 1
        ELSE 0
    END AS is_late

FROM orders AS o
JOIN customers AS c
    ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01';


-- ------------------------------------------------------------------
-- 2. products_clean: every product with an English category name
-- ------------------------------------------------------------------
DROP VIEW IF EXISTS products_clean;

CREATE VIEW products_clean AS
SELECT
    p.product_id,
    -- COALESCE returns the first value that isn't NULL:
    -- English name if there's a translation, else the Portuguese name,
    -- else 'unknown' for products with no category at all.
    -- The CASE fills in English names for the 2 categories missing
    -- from the translation table (found with 05_untranslated.sql).
    COALESCE(t.product_category_name_english,
             CASE p.product_category_name
                 WHEN 'pc_gamer' THEN 'pc_gamer'
                 WHEN 'portateis_cozinha_e_preparadores_de_alimentos'
                     THEN 'kitchen_portables_and_food_preparers'
             END,
             p.product_category_name,
             'unknown') AS category,
    p.product_weight_g
FROM products AS p
LEFT JOIN category_translation AS t          -- LEFT JOIN keeps products
    ON t.product_category_name = p.product_category_name;  -- with no match


-- ------------------------------------------------------------------
-- 3. reviews_clean: exactly one review per order
-- ------------------------------------------------------------------
-- A few orders have more than one review. We keep the most recent one.
DROP VIEW IF EXISTS reviews_clean;

CREATE VIEW reviews_clean AS
SELECT order_id, review_score, review_creation_date
FROM (
    SELECT
        order_id,
        review_score,
        review_creation_date,
        -- ROW_NUMBER() numbers the reviews 1, 2, 3... inside each order
        -- (PARTITION BY order_id), newest first (ORDER BY ... DESC).
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY review_answer_timestamp DESC
        ) AS review_rank
    FROM reviews
)
WHERE review_rank = 1;   -- keep only the newest review for each order
