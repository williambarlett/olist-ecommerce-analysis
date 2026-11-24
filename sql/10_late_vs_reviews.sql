SELECT
    CASE WHEN o.is_late = 1 THEN 'late' ELSE 'on time' END     AS delivery,
    COUNT(*)                                                    AS orders,
    ROUND(AVG(rv.review_score), 2)                              AS avg_review,
    ROUND(100.0 * AVG(CASE WHEN rv.review_score <= 2
                           THEN 1 ELSE 0 END), 1)               AS pct_bad_reviews
FROM orders_clean AS o
JOIN reviews_clean AS rv
    ON rv.order_id = o.order_id
WHERE o.is_late IS NOT NULL
GROUP BY delivery;