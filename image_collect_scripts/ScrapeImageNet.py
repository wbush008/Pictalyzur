import os
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError


def scrape_term(category, imnet_lst, path):
    width = 256
    height = 256

    BASE_PATH = os.path.join('../', path, category)

    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

    for i, image in enumerate(imnet_lst):

        if i % 500 == 1:
            print category + ': ' + str(i)

        url = image
        title = image.split('/')[-1]

        try:
            image_r = requests.get(url, allow_redirects=False)
        except ConnectionError, e:
            continue

        file = open(os.path.join(BASE_PATH, '%s') % title, 'w')

        try:
            Image.open(StringIO(image_r.content)).resize((width, height), Image.ANTIALIAS).save(file, 'JPEG')
        except IOError, e:
            os.remove(os.path.join(BASE_PATH, '%s') % title)
        finally:
            file.close()


if __name__ == '__main__':

    scrape_term('IMN_bicycles',
                requests.get('http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n04126066').text.split(), 
                'imnet_cats')
