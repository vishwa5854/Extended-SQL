-- Referred from Paper-2 Q.2
-- One may want to identify those months that
-- were “significant” for the sales of a product: “For each
-- product and sales, show the product’s average
-- sale before and after each month.” (trends)

-- SQL
drop view B1;
create view B1 as
select x.prod, x.month, avg(y.quant) as xx
from Sales x,
     Sales y
where x.prod = y.prod
  and x.month > y.month
group by x.prod, x.month;

drop view B2;
create view B2 as
select x.prod, x.month, avg(y.quant) as yy
from Sales x,
     Sales y
where x.prod = y.prod
  and x.month < y.month
group by x.prod, x.month;

select B1.prod, B1.month, xx, yy
from B1,
     B2
where B1.prod = B2.prod
  and B1.month = B2.month;

-- ESQL
select prod,
       month,
       avg(X.quant),
       avg(Y.quant)
from Sales
group by prod, month; X , Y
such that X.prod=prod and
X.month<month,
Y.prod=prod and
Y.month>month
