'''
helper functions
'''
import psycopg2

from flask_test.my_secrets import (
    GOOGLE_CUSTOM_SEARCH_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID,
    DB_HOST_NAME, DB_USER_NAME, DB_PASSWORD, DB_NAME, DB_PORT
)

def get_connection(**kwargs):
    '''
    return connection attached to DB
    kwargs: host, user, password, database, port
    '''

    # access info
    if kwargs:
        host = kwargs.get('host')
        assert host != None
        user = kwargs.get('user')
        assert user != None
        password = kwargs.get('password')
        assert password != None
        database = kwargs.get('database')
        assert database != None
        port = kwargs.get('port')
        assert port != None
    else:
        host = DB_HOST_NAME
        user = DB_USER_NAME
        password = DB_PASSWORD
        database = DB_NAME
        port = DB_PORT

    # conn
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )

    return connection
