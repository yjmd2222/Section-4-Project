'''
get image links and upload
'''
import requests

from flask_test.helpers import get_connection
from flask_test.my_secrets import (
    GOOGLE_CUSTOM_SEARCH_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID
)

def get_image_links(query='correct sitting posture', count=100):
    serachType = 'image'
    links = []
    for page in range(1, count+1):
        start = (page - 1) * 10 + 1
        url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_CUSTOM_SEARCH_API_KEY}&cx={GOOGLE_CUSTOM_SEARCH_ENGINE_ID}&q={query}&start={start}&searchType={serachType}'
        data = requests.get(url).json()

        results = data.get("items")
        if results is None:
            print('probably reached the limit')
            break
        try:
            for result in results:
                print(result['link'])
                links.append(result['link'])
        except:
            print('no link in result')

    return links

def send_links_to_db(links, posture):
    connection = get_connection()
    cursor = connection.cursor()

    # create table
    sql_create_table = '''
    CREATE TABLE IF NOT EXISTS links (
        Id SERIAL PRIMARY KEY,
        links VARCHAR(1000),
        posture VARCHAR(15)
    )
    '''
    cursor.execute(sql_create_table)

    # insert data
    sql_insert_data = r'''
    INSERT INTO links (links, posture) VALUES (%s, %s)
    '''
    data = [(link, posture) for link in links]
    cursor.executemany(sql_insert_data, data)

    connection.commit()
    cursor.close()
    connection.close()

    print('successfully sent data')
