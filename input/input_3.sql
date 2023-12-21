-- SQL:
SELECT cust, sum(quant), avg(quant), max(quant), min(quant), count(quant)
FROM sales
WHERE state = 'NY'
GROUP BY cust;

-- EMF:
SELECT cust, sum(1.quant), avg(1.quant), max(1.quant), min(1.quant), count(1.quant)
FROM sales
GROUP BY cust; 1
SUCH THAT 1.state = 'NY' AND 1.cust = cust;
