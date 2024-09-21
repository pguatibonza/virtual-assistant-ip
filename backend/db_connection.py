import pymysql.cursors

# Connect to the database
def fetch_data(query):
    connection = None
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='password',
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