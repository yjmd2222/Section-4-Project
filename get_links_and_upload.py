'''
get image links and upload
'''
# import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from flask_test.helpers import get_connection
# from flask_test.my_secrets import (
#     GOOGLE_CUSTOM_SEARCH_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID
# )

# def get_image_links(query='correct sitting posture', count=100):
#     serachType = 'image'
#     links = []
#     for page in range(1, count+1):
#         start = (page - 1) * 10 + 1
#         url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_CUSTOM_SEARCH_API_KEY}&cx={GOOGLE_CUSTOM_SEARCH_ENGINE_ID}&q={query}&start={start}&searchType={serachType}'
#         data = requests.get(url).json()

#         results = data.get("items")
#         if results is None:
#             print('probably reached the limit')
#             break
#         try:
#             for result in results:
#                 print(result['link'])
#                 links.append(result['link'])
#         except:
#             print('no link in result')

#     return links

def send_links_to_db(links, posture):
    connection = get_connection()
    cursor = connection.cursor()

    # create table
    sql_create_table = '''
    CREATE TABLE IF NOT EXISTS links (
        Id SERIAL PRIMARY KEY,
        link VARCHAR(10000),
        posture VARCHAR(15),
        processed BIT(1)
    )
    '''
    cursor.execute(sql_create_table)

    # insert data
    sql_insert_data = r'''
    INSERT INTO links (link, posture, processed) VALUES (%s, %s, B'%s')
    '''
    data = [(link, posture, 0) for link in links]
    # print(data)
    cursor.executemany(sql_insert_data, data)

    connection.commit()
    cursor.close()
    connection.close()

    print('successfully sent data')

driver = webdriver.Chrome()

PAUSE = 3

postures = ['normal', 'forward_head', 'leaning']
query_dict_list = [{'normal': ['correct sitting posture', '바른 앉은 자세']}, {'forward_head': ['거북목', 'forward head posture']}, {'leaning': ['leaning back in chair', '의자 기대 앉기']}]
for idx, query_dict in enumerate(query_dict_list):
    for queries in query_dict.values():
        for query in queries:
            driver.get(f'https://www.google.com/search?q={query}&tbm=isch')
            driver.maximize_window()
            time.sleep(PAUSE)

            script_height = 'return document.body.scrollHeight'
            script_scroll_down = "window.scrollTo(0, document.body.scrollHeight);"

            height = driver.execute_script(script_height)

            for i in range(10):
                driver.execute_script(script_scroll_down)
                time.sleep(PAUSE)
                new_height = driver.execute_script(script_height)
                time.sleep(PAUSE)
                if new_height == height:
                    break

                height = new_height

            img_tags = driver.find_elements(By.CLASS_NAME, 'rg_i.Q4LuWd')
            thumb_nail_links = [tag.get_attribute('src') for tag in img_tags]
            thumb_nail_links = [link for link in thumb_nail_links if link is not None and len(link) < 1000]

            send_links_to_db(thumb_nail_links, postures[idx])
    time.sleep(PAUSE)

driver.quit()

