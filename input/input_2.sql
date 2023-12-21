-- SQL:
SELECT cust, prod, avg(quant), max(quant)
FROM sales
GROUP BY cust,prod;

-- EMF:
SELECT cust, prod, avg(quant), max(quant)
FROM sales
GROUP BY cust, prod;
