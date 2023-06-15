from flask_test.get_links_and_upload import get_image_links, send_links_to_db

posture = 'forward head'

links = get_image_links()
send_links_to_db(links, posture)