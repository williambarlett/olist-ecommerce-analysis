WITH order_revenue AS (
    SELECT order_id, SUM(payment_value) AS revenue
    FROM payments
    GROUP BY order_id
)
SELECT
    o.purchase_month,
    COUNT(*)                    AS orders,
    ROUND(SUM(r.revenue), 0)    AS revenue,
    ROUND(AVG(r.revenue), 2)    AS avg_order_value
FROM orders_clean AS o
LEFT JOIN order_revenue AS r
    ON r.order_id = o.order_id
GROUP BY o.purchase_month
ORDER BY o.purchase_month;