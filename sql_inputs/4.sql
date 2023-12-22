-- Show for each customer and product combination, the total sales quantities for 4
-- quarters, Q1, Q2 (in four separate columns) – Q1 being the first 3 months
-- of the year (Jan, Feb & Mar), Q2 the next 3 months (Apr, May & Jun), and so on –
-- ignore the YEAR component of the dates (i.e., 3/11/2001 is considered the same date
-- as 3/11/2002, etc.). Also compute the average for the q1, q2, total of the first two quarters (again ignoring
-- the YEAR component, meaning simply compute AVG) along with the total quantities
-- (SUM) and the counts (COUNT).
-- Referred from CS561

-- ESQL
SELECT cust, prod, sum_1_quant, sum_2_quant, sum_1_quant + sum_2_quant, count_1_quant + count_2_quant, sum_1_quant / count_1_quant, sum_2_quant / count_2_quant
FROM sales
group by cust, prod; 1, 2
such that 1.cust==cust and 1.prod==prod and 1.month>=1 and 1.month<=3
2.cust==cust and 2.prod==prod and 2.month>=4 and 2.month<=6



-- SQL
with monthly_sales as
         (select cust, prod, month, sum(quant) as total, count(prod) as count_sale
          from sales
          group by cust, prod, month
          order by cust, prod, month),

     q1_sales as
         (select cust, prod, sum(total) as q1_tot, sum(count_sale) as q1_count
          from monthly_sales
          where month <= 3 and month>=1
          group by cust, prod),

     q2_sales as
         (select cust, prod, sum(total) as q2_tot, sum(count_sale) as q2_count
          from monthly_sales
          where month >= 4
            and month <= 6
          group by cust, prod),


     combined_table as
         (select q1_sales.cust,
                 q1_sales.prod,
                 q1_tot,
                 q2_tot,
                 q1_count,
                 q2_count,
                 (q1_tot + q2_tot )         as total,
                 (q1_count + q2_count ) as count
          from q1_sales
                   join q2_sales on q1_sales.cust = q2_sales.cust and q1_sales.prod = q2_sales.prod)

select cust            as CUSTOMER,
       prod            as PRODUCT,
       q1_tot,
       q2_tot,
       total,
       count,
       q1_tot / q1_count,
       q2_tot / q2_count
from combined_table;