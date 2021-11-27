import psycopg2


def set_connection():
    return psycopg2.connect(
        user='postgres',
        password='postgres',
        host='127.0.0.1',
        port='5432',
        database='postgres'
    )

