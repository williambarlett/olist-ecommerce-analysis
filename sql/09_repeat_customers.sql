WITH customer_orders AS (
    SELECT customer_unique_id, COUNT(*) AS n_orders
    FROM orders_clean
    GROUP BY customer_unique_id
)
SELECT
    COUNT(*)                                          AS customers,
    SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END)    AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END)
          / COUNT(*), 1)                              AS pct_repeat,
    MAX(n_orders)                                     AS most_orders_one_customer
FROM customer_orders;