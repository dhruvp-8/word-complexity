import gevent
from gevent import monkey
import requests
import time

start_time = time()
monkey.patch_all()


urls = ['http://www.dictionary.com/browse/sit', 'http://phrasefinder.io/search?corpus=eng-us&query=The cat perched']


def print_head(url):
    print('Starting %s' % url)
    data = requests.get(url).text
    print('%s: %s bytes: %r' % (url, len(data), data[:50]))

jobs = [gevent.spawn(print_head, _url) for _url in urls]

gevent.wait(jobs)

end_time = time() - sart