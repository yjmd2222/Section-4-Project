import psycopg2
from flask_test.get_image_links import get_image_links
from flask_test.my_secrets import DB_HOST_NAME, DB_USER_NAME, DB_PASSWORD, DB_NAME

links = get_image_links()

# connection info
host = DB_HOST_NAME
user = DB_USER_NAME
password = DB_PASSWORD
database = DB_NAME

# conn
connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# cur
cursor = connection.cursor()

# create table
sql_create_table = f'''
CREATE TABLE IF NOT EXISTS Links (
    Id SERIAL PRIMARY KEY,
    Link VARCHAR(1000)
)
'''
cursor.execute(sql_create_table)

sql_insert = f'''
INSERT INTO Links (Link) VALUES %s
'''
cursor.executemany(sql_insert, links) # once

# commit and close
connection.commit()
cursor.close()
connection.close()
