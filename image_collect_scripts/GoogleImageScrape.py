import json
import os
import time
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError


def scrape_term(category, query_bases, mods, path):
    for query_base in query_bases:
        print query_base
        for mod in mods:
            query = query_base+mod
            BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
                     'v=1.0&q=' + query + '&start=%d'

            width = 256
            height = 256

            BASE_PATH = os.path.join('../', path, category)

            if not os.path.exists(BASE_PATH):
                os.makedirs(BASE_PATH)

            start = 0
            while start < 60:
                r = requests.get(BASE_URL % start)

                for image_info in json.loads(r.text)['responseData']['results']:
                    url = image_info['unescapedUrl']
                    try:
                        image_r = requests.get(url)
                    except ConnectionError, e:
                        print 'could not download %s' % url
                        continue

                    title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '')

                    file = open(os.path.join(BASE_PATH, '%s.jpg') % title, 'w')
                    if 'stock' in BASE_PATH:
                        pass
                    else:
                        try:
                            Image.open(StringIO(image_r.content)).resize((width, height), 
                                                                         Image.ANTIALIAS).save(file, 'JPEG')
                        except IOError, e:
                            os.remove(os.path.join(BASE_PATH, '%s.jpg') % title)
                            continue
                        finally:
                            file.close()

                start += 4

                time.sleep(1.5)


if __name__ == '__main__':

    """
    Usage
    """
    scrape_term('gardening', ['backyard garden', 'flower outside',
                              'planting vegetable', 'vegetable garden',
                              'flower garden', 'home grown', 'garden',
                              'herb garden', 'gardening tools outside',
                              'flower closeup', 'backyard orchard', ],
                ['', 'flickr', 'instagram', 'tumblr'], 'image_cats')
