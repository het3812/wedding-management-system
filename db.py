import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv("MYSQLHOST"),
    port=int(os.getenv("MYSQLPORT")),
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQLDATABASE")
)

cursor = connection.cursor(dictionary=True)

def execute_query(query, values=None):
    cursor.execute(query, values or ())
    return cursor.fetchall()

def execute_update(query, values=None):
    cursor.execute(query, values or ())
    connection.commit()