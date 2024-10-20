# this file makes calls to the database & outputs them onto json files
import psycopg2
import json

# Establishing Connection
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="9089223654",
    host="database-1.cqqwg6frglat.us-west-2.rds.amazonaws.com",
    port="5432"
)

curr = conn.cursor()

# we want to call all courses that are required for a degree audit 