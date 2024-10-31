import os
import logging
import pymysql.cursors

logger = logging.getLogger(__name__)

USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')

# Determine if the code is running inside a Docker container
def get_mysql_host():
    if os.path.exists('/.dockerenv'):
        # Running inside Docker
        return "host.docker.internal"
    else:
        # Running locally
        return "localhost"

# Use the function to set the MySQL host
HOST = get_mysql_host()
logger.warning(f"HOST: {HOST}")

# Connect to the database
def fetch_data(query):
    connection = None
    try:
        connection = pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database='calificador_anonimo',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection:
            connection.close()