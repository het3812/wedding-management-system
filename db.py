"""
Database connection helper for Wedding Management System
Uses mysql-connector-python for MySQL (XAMPP compatible)
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_db_connection():
    """
    Creates and returns a MySQL database connection.
    Caller must close the connection when done.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


def execute_query(query, params=None, fetch_one=False):
    """
    Execute a query and return results.
    Use for SELECT operations.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)  # Returns rows as dicts
        cursor.execute(query, params or ())
        result = cursor.fetchone() if fetch_one else cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()


def execute_update(query, params=None):
    """
    Execute INSERT, UPDATE, DELETE and return last insert id if applicable.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv("MYSQLHOST"),
    port=os.getenv("MYSQLPORT"),
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