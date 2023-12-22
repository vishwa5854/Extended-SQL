-- Question - 4
DROP VIEW IF EXISTS AvgSales;
CREATE VIEW AvgSales AS
SELECT
  prod,
  month,
  AVG(quant) AS avg_quant
FROM
  Sales
WHERE
  year = 2018
GROUP BY
  prod, month;

SELECT
  S.prod,
  S.month,
  COUNT(CASE WHEN P.month = S.month - 1 AND P.quant > A.avg_quant THEN 1 END) AS Prev_Month_Greater,
  COUNT(CASE WHEN N.month = S.month + 1 AND N.quant > A.avg_quant THEN 1 END) AS Next_Month_Greater
FROM
  Sales S
  LEFT JOIN Sales P ON S.prod = P.prod AND P.year = 2018
  LEFT JOIN Sales N ON S.prod = N.prod AND N.year = 2018
  INNER JOIN AvgSales A ON S.prod = A.prod AND S.month = A.month
WHERE
  S.year = 2018 AND S.month > 1 AND S.month < 12
GROUP BY
  S.prod, S.month;
