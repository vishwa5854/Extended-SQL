FROM postgres
COPY db-dumps/sales.sql /docker-entrypoint-initdb.d/
