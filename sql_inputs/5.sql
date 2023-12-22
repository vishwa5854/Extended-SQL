-- Referred from Paper-2 Question 6 (But slightly tweaked to include having clause)
-- For each customer, show for each product the customer’s average sale, and the other customers’ average sale
-- (for the same product). Also show only the customers whose sales could improve compared to other customers' avg sale

-- SQL
with t1 as (select C1.cust,
                   C1.prod,
                   avg(C1.quant)              as cust_avg_sale,
                   (select avg(C2.quant)
                    from Sales C2
                    where C2.prod = C1.prod
                      and C2.cust != C1.cust) as other_custs_avg_sale
            from Sales C1
            group by C1.cust, C1.prod)
select *
from t1
where other_custs_avg_sale > cust_avg_sale;

-- ESQL
select cust, prod, avg(X.quant), avg(Y.quant)
from Sales
group by cust, prod; X, Y
such that X.cust = cust and X.prod = prod,
Y.prod = prod and Y.cust != cust
having avg(Y.quant) > avg(X.quant);
