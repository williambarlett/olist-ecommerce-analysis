-- 04_check_views.sql
-- Sanity checks on the clean views. Each (SELECT ...) is a small
-- sub-query that returns one number; together they make one summary row.
SELECT
    (SELECT COUNT(*) FROM orders_clean)                           AS orders,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM orders_clean) AS customers,
    (SELECT COUNT(*) FROM orders_clean WHERE delivered_at IS NULL) AS missing_delivery_date,
    (SELECT ROUND(AVG(delivery_days), 1) FROM orders_clean)       AS avg_delivery_days,
    (SELECT ROUND(100.0 * AVG(is_late), 1) FROM orders_clean)     AS pct_late,
    (SELECT COUNT(*) FROM products_clean WHERE category = 'unknown') AS products_no_category,
    (SELECT COUNT(*) FROM products_clean
       WHERE category NOT IN (SELECT product_category_name_english
                              FROM category_translation)
         AND category <> 'unknown')                               AS products_untranslated;
