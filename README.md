# ESQL

Extended-SQL introduces a new operator called PHI to standard SQL to extend & simplify SQL queries (especially OLAP queries, including hierarchies, trends, etc).

This project is based on the philosophy of _**"Succint queries lead to efficient evaluation"**_.

Extended-SQL lets you decouple group by attributes and aggregate functions by introducing a operation called as _**PHI**_ in relational algebra, 
and a new clause called as _**SUCH THAT**_ which operates on a new term called as _**GROUPING VARIABLES**_.

# Mission
The mission of this project is to build a query processing engine for Ad-Hoc OLAP
queries. The query construct is based on an extended SQL syntax known as MF and
EMF queries (i.e., Multi-Feature and Extended Multi-Feature queries).

# Normal SQL vs Extended-SQL <br> 
## (TLDR; Extended-SQL is much more _**Simpler, Succint & Blazingly Fast**_)
Consider this OLAP table schema which records sales.
### **sales (cust, prod, day, month, year, state, quant, date)**

1. For each customer and product find avg quantity in states of "NY" and "CT".
    Traditional SQL query would look something like this involving multiple **expensive table JOINS**
    ```SQL
    WITH t1 as (
        SELECT cust, prod, avg(quant)
        FROM sales
        WHERE state = 'NY'
        GROUP BY cust, prod
    ), t2 as (
        SELECT cust, prod, avg(quant)
        FROM sales
        WHERE state = 'CT'
        GROUP BY cust, prod
    ) select * from t1 inner join t2 on t1.cust = t2.cust and t1.prod = t2.prod;
    ```
    
    Extended-SQL Version (Note that this is an MF-Query, more on this later)
    ```SQL
    SELECT cust, prod, avg(1.quant) as NY_avg_quant, avg(2.quant) as CT_avg_quant
    FROM sales
    GROUP BY cust, prod; 1, 2
    SUCH THAT 1.state = 'NY',
    2.state = 'CT';
    ```
2. One may want to identify those months that were “significant” for the sales of a product: “For each product and sales, show the product’s average sale before and after each month.” (trends)
   Traditional SQL query would look something like this involving multiple **expensive table JOINS**
    ```SQL
    DROP VIEW B1;
    CREATE VIEW B1 as
    SELECT x.prod, x.month, avg(y.quant) as xx
    FROM Sales x,
         Sales y
    WHERE x.prod = y.prod
      and x.month > y.month
    GROUP BY x.prod, x.month;
    
    DROP VIEW B2;
    CREATE VIEW B2 as
    SELECT x.prod, x.month, avg(y.quant) as yy
    FROM Sales x,
         Sales y
    WHERE x.prod = y.prod
      and x.month < y.month
    GROUP BY x.prod, x.month;
    
    SELECT B1.prod, B1.month, xx, yy
    FROM B1,
         B2
    WHERE B1.prod = B2.prod
      and B1.month = B2.month;
    ```
    
    Extended-SQL Version (Note that this is an EMF-Query, more on this later)
    ```SQL
    SELECT prod,
       month,
       avg(X.quant),
       avg(Y.quant)
    FROM Sales
    GROUP BY prod, month; X , Y
    SUCH THAT X.prod = prod and X.month < month,
    Y.prod = prod and Y.month > month;
    ```

# Pre-requisites
1. You need postgres to be running either in your local or modify .env to point to a running postgres instance
2. Set up the username, password so that .env matches

# How to run ?
You need to have postgres running in your local machine or change the configuration of postgres in the .env file.
1. Create a virtual environment to run the code.
```bash
 python3 -m venv esql
```
2. Spawn a shell inside the created virtual environment.
```bash
source esql/bin/activate
```
3. Install dependencies
```bash
pip3 install -r requirements.txt
```
4. Run the code
```bash
python3 generator.py <input_file> <options>
```

# Sample Usage
1. If you would like to run an emf query
```bash
python3 generator.py emf-inputs/1.txt
```
2. If you would like to run an mf query
```bash
python3 generator.py mf-inputs/1.txt mf
```
3. If you just wanna generate the code but don't want to run it automatically
```bash
python3 generator.py emf-inputs/1.txt dont-run
```

# Installing Postgres & PGAdmin
I use docker to spin up Postgres and PGAdmin in my local using the <strong>postgres-pgadmin-compose.yml</strong>.
The below command will spin up a docker compose with both PGAdmin and Postgres with credentials matching in .env file.
```bash
docker compose -f postgres-pgadmin-compose.yml up -d
```
