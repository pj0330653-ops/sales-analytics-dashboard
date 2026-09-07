-- queries.sql
-- Business-question SQL run against sales.db (table: sales)
-- Load the db first: python load_db.py
-- Run any query:      sqlite3 sales.db < queries.sql

-- 1. Total revenue, orders and average order value
SELECT
    COUNT(DISTINCT order_id)      AS total_orders,
    ROUND(SUM(net_sales), 2)      AS total_revenue,
    ROUND(SUM(net_sales) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM sales;

-- 2. Monthly revenue trend
SELECT
    order_month,
    ROUND(SUM(net_sales), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders
FROM sales
GROUP BY order_month
ORDER BY order_month;

-- 3. Top 5 regions by revenue
SELECT
    region,
    ROUND(SUM(net_sales), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders
FROM sales
GROUP BY region
ORDER BY revenue DESC
LIMIT 5;

-- 4. Best-selling products by units sold
SELECT
    product,
    category,
    SUM(quantity)             AS units_sold,
    ROUND(SUM(net_sales), 2)  AS revenue
FROM sales
GROUP BY product, category
ORDER BY units_sold DESC
LIMIT 10;

-- 5. Sales rep leaderboard (top performer per region)
SELECT region, sales_rep, revenue FROM (
    SELECT
        region,
        sales_rep,
        ROUND(SUM(net_sales), 2) AS revenue,
        RANK() OVER (PARTITION BY region ORDER BY SUM(net_sales) DESC) AS rnk
    FROM sales
    GROUP BY region, sales_rep
)
WHERE rnk = 1;

-- 6. Customer segment contribution to revenue
SELECT
    customer_segment,
    ROUND(SUM(net_sales), 2) AS revenue,
    ROUND(100.0 * SUM(net_sales) / (SELECT SUM(net_sales) FROM sales), 2) AS pct_of_total
FROM sales
GROUP BY customer_segment
ORDER BY revenue DESC;

-- 7. Discount impact: revenue lost to discounts by category
SELECT
    category,
    ROUND(SUM(discount_amount), 2) AS total_discount_given,
    ROUND(SUM(gross_sales), 2)     AS gross_sales,
    ROUND(100.0 * SUM(discount_amount) / SUM(gross_sales), 2) AS discount_pct_of_gross
FROM sales
GROUP BY category
ORDER BY total_discount_given DESC;

-- 8. Preferred payment mode by customer segment
SELECT
    customer_segment,
    payment_mode,
    COUNT(*) AS order_count
FROM sales
GROUP BY customer_segment, payment_mode
ORDER BY customer_segment, order_count DESC;
