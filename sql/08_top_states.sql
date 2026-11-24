WITH order_revenue AS (
    SELECT order_id, SUM(payment_value) AS revenue
    FROM payments
    GROUP BY order_id
)
SELECT
    o.customer_state                         AS state,
    COUNT(*)                                 AS orders,
    ROUND(SUM(r.revenue), 0)                 AS revenue,
    ROUND(100.0 * SUM(r.revenue)
          / SUM(SUM(r.revenue)) OVER (), 1)  AS pct_of_revenue,
    ROUND(AVG(o.delivery_days), 1)           AS avg_delivery_days
FROM orders_clean AS o
LEFT JOIN order_revenue AS r
    ON r.order_id = o.order_id
GROUP BY o.customer_state
ORDER BY revenue DESC
LIMIT 10;