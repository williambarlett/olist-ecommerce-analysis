SELECT strftime('%Y-%m', order_purchase_timestamp) AS month,
       COUNT(*) AS num_orders
FROM orders
GROUP BY month
ORDER BY month;