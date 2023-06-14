import requests
from flask_test.my_secrets import GOOGLE_CUSTOM_SEARCH_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID

def get_image_links(query='correct sitting posture', count=100):
    serachType = 'image'
    for page in range(1, count+1):
        start = (page - 1) * 10 + 1
        url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_CUSTOM_SEARCH_API_KEY}&cx={GOOGLE_CUSTOM_SEARCH_ENGINE_ID}&q={query}&start={start}&searchType={serachType}'
        data = requests.get(url).json()

        results = data.get("items")
        print(results)
        for result in results:
            try:
                print(result['link'])
                return result['link']
            except:
                print('no link in result')
                return None
            
if __name__ == '__main__':
    get_image_links()
