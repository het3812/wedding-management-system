import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT")),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )

def execute_query(query, values=None):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(query, values or ())
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result

def execute_update(query, values=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, values or ())
    connection.commit()

    cursor.close()
    connection.close()