from flask_test.get_links_and_upload import get_image_links, send_links_to_db

postures = ['normal', 'forward_head', 'leaning']
search_terms = ['correct sitting posture', 'forward head posture', 'leaning back in chair']

for idx, posture in enumerate(postures):
    links = get_image_links(query=search_terms[idx])
    send_links_to_db(links, posture)
