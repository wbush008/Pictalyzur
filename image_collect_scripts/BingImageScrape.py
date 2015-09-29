from bs4 import BeautifulSoup
import argparse
import re
import urllib2


def get_soup(url, header):
    return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)))

image_type = "outdoor_nat"
header = {'User-Agent': 'Mozilla/5.0'}


def scrape_term(query):

    query = query.split()
    query = '+'.join(query)
    url = "http://www.bing.com/images/search?q="+query
    print url

    soup = get_soup(url, header)

    cntr = 0
    images = [a['src'] for a in soup.find_all("img", {"src": re.compile("bing.net")})]

    for img in images:
        raw_img = urllib2.urlopen(img).read()

        DIR = "/home/will/code/outdoor_nat/"
        cntr += 1

        f = open(DIR + query + "_" + str(cntr) + ".jpg", 'wb')
        f.write(raw_img)
        f.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('query')

    scrape_term(parser.parse_args().query)
