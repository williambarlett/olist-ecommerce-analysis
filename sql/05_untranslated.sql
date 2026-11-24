SELECT category, COUNT(*) AS products
FROM products_clean
WHERE category NOT IN (SELECT product_category_name_english FROM category_translation)
  AND category <> 'unknown'
GROUP BY category;