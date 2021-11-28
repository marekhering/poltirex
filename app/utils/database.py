from urllib.parse import urlparse
import psycopg2
import os


def set_connection():
    result = urlparse(os.getenv("DATABASE_URL"))
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    print(result, database, port, hostname, username, password)

    return psycopg2.connect(
        user=username,
        password=password,
        host=hostname,
        port=port,
        database=database
    )

