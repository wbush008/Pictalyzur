import json
import os
import requests
import concurrent.futures
import argparse
from PIL import Image
from StringIO import StringIO

user_image_path = '../bin/jpgs/users/'


def crawl(username, items=[], max_id=None):
    '''
    input: username
    return: list of media items in the users feed
    '''

    url = 'http://instagram.com/' + username + '/media' + \
        ('?&max_id=' + max_id if max_id is not None else '')
    media = json.loads(requests.get(url).text)

    items.extend([curr_item for curr_item in media['items']])

    if 'more_available' not in media or media['more_available'] is False:
        return items
    else:
        max_id = media['items'][-1]['id']
        return crawl(username, items, max_id)


def download(item, save_dir='./'):
    '''
    input: list of media items (json), directory to save images
    return: None

    Takes a list of JSONs with media information from Instagram, and
    save that media to a local folder.  Resizes images to 256*256
    for easy use with caffe.
    '''

    width = 256
    height = 256
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    url = item[item['type'] + 's']['low_resolution']['url']
    base_name = url.split('/')[-1]

    file_path = os.path.join(save_dir, base_name)

    if '.jpg' not in file_path:
        pass
    else:
        with open(file_path, 'wb') as file:
            print 'Downloading ' + base_name
            bytes = requests.get(url).content
            Image.open(StringIO(bytes)).resize((width, height), Image.ANTIALIAS).save(file, 'JPEG')


def scrape_user(username):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_item = dict((executor.submit(download, item,
                                               user_image_path + username),
                                               item) for item in crawl(username))

        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            url = item[item['type'] + 's']['low_resolution']['url']

            if future.exception() is not None:
                print '%r generated an exception: %s' % (url, future.exception())


if __name__ == '__main__':

    """
    Usage: python ScrapeUser.py <username>
    """
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('username')

    scrape_user(parser.parse_args().username)
