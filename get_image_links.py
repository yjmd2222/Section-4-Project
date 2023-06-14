import requests
from my_secrets import GOOGLE_CUSTOM_SEARCH_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID

query = 'correct sitting posture'
page = 1
start = (page - 1) * 10 + 1
serachType = 'image'
url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_CUSTOM_SEARCH_API_KEY}&cx={GOOGLE_CUSTOM_SEARCH_ENGINE_ID}&q={query}&start={start}&searchType={serachType}'
data = requests.get(url).json()

results = data.get("items")
for result in results:
    try:
        print(result['link'])
    except:
        print('no link in result')