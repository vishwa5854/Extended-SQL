-- Suppose that we want to identify “good” and “bad”
-- months of a product’s sales, as well as interesting
-- irregularities: “For each product show each month’s
-- total sales as percentage of this product’s year-long
-- total sales.” (hierarchies)
-- Referred from Paper-2 Q4

-- SQL
WITH t1 as (
    select prod, month, year, sum(quant) as x_quant
    from sales
    group by prod, month, year
), t2 as (
    select prod, year, sum(quant) as y_quant
    from sales
    group by prod, year
) select t1.prod, month, t1.year, (CAST(t1.x_quant AS numeric) / t2.y_quant) from
t1 inner join t2 on t1.prod=t2.prod and t1.year=t2.year order by prod, year, month;

-- ESQL
select prod,
       month,
       year,
       sum(X.quant) / sum(Y.quant)
from Sales
group by prod, month, year; X,Y
such that
X.prod=prod and X.month=month and X.year=year,
Y.prod=prod and Y.year=year;
