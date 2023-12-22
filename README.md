# ESQL

Extended SQL lets you decouple group by attributes and aggregate functions by introducing a operation called as PHI in relational algebra, 
and a new clause called as SUCH THAT.

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
# Installing Postgres & PGAdmin
I use docker to spin up Postgres and PGAdmin in my local using the <strong>postgres-pgadmin-compose.yml</strong>.
The below command will spin up a docker compose with both PGAdmin and Postgres with credentials matching in .env file.
```bash
docker compose -f postgres-pgadmin-compose.yml up -d
```
