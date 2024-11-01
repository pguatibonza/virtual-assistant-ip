import os
import socket
import logging
import pymysql.cursors

logger = logging.getLogger(__name__)

USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')

def is_reachable(host, port=3306):
    """Check if the specified host and port are reachable."""
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def get_database_host():
    # Check if running inside a Docker container
    if os.path.exists('/.dockerenv'):
        # Test if host.docker.internal is reachable
        if is_reachable("host.docker.internal"):
            return "host.docker.internal"
        else:
            # Assume we are on a Linux-based VM with --network host
            return "localhost"
    else:
        # Running locally (e.g., `streamlit run main.py`)
        return "localhost"

HOST = get_database_host()
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
            