SELECT
    p.category,
    COUNT(DISTINCT oi.order_id)  AS orders,
    COUNT(*)                     AS items_sold,
    ROUND(SUM(oi.price), 0)      AS item_revenue,
    ROUND(AVG(oi.price), 2)      AS avg_item_price
FROM order_items AS oi
JOIN orders_clean AS o
    ON o.order_id = oi.order_id
JOIN products_clean AS p
    ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY item_revenue DESC
LIMIT 10;