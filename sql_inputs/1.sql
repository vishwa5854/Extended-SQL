-- For each customer find all the aggregates in "NY",
-- find all the aggregates in "CT"
-- This is referred from quizz 1

-- SQL:
WITH t1 as (
    SELECT cust, sum(quant), avg(quant), max(quant), min(quant), count(quant)
    FROM sales
    WHERE state = 'NY'
    GROUP BY cust
), t2 as (
    SELECT cust, sum(quant), avg(quant), max(quant), min(quant), count(quant)
    FROM sales
    WHERE state = 'CT'
    GROUP BY cust
) select * from t1 inner join t2 on t1.cust = t2.cust;


-- ESQL - EMF
select cust, sum_1_quant, avg_1_quant, max_1_quant, min_1_quant, count_1_quant, cust, sum_2_quant, avg_2_quant, max_2_quant, min_2_quant, count_2_quant
from sales
group by cust; 1, 2
such that 1.state=='NY' and 1.cust==cust
2.state=='CT' and 2.cust==cust;


-- ESQL - MF
select cust, sum_1_quant, avg_1_quant, max_1_quant, min_1_quant, count_1_quant, cust, sum_2_quant, avg_2_quant, max_2_quant, min_2_quant, count_2_quant
from sales
group by cust; 1, 2
such that 1.state=='NY'
2.state=='CT';
