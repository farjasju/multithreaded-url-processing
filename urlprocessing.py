import concurrent.futures
import urllib.request
from urllib.parse import urlparse
import time
import csv
import os
from lazypool import LazyThreadPoolExecutor
from ural import ensure_protocol


WORKERS = 20
CSV_FILE = os.path.join('data', 'source_urls.csv')


def domain_from_url(url):
    # print('   -> DOMAIN FROM URL:', ensure_protocol(url)[:30], type(url))
    parsed_url = urlparse(ensure_protocol(url))
    result = parsed_url.netloc.split('@')
    if len(result) == 1:
        return result[0]
    else:
        return result[1]


class CustomIterator(object):
    def __init__(self, urls):
        self.urls = urls
        self.current_domains = set()
        self.todo_later = set()

    def __iter__(self):
        return self

    def mark_as_complete(self, url):
        # print('   ITERATOR : MARK AS COMPLETE', url[:30])
        self.current_domains.discard(domain_from_url(url))
        # print('   REMOVING', domain_from_url(url), 'from current_domains')

    def __next__(self):
        url = next(self.urls)
        self.current_domains.add(domain_from_url(url))
        # print('ADDING', domain_from_url(url), 'to current_domains')
        return url


def task(url):
    if url is None:
        print('   [task]: url is None')
    try:
        time.sleep(1)
        # print('   [task]')
        return (url, domain_from_url(url))
    except Exception as e:
        return (url, 'failure: ' + str(e))


def multithreaded(task, urls, workers):
    iterator = CustomIterator(urls)
    executor = LazyThreadPoolExecutor(workers)
    for result in executor.map(task, iterator):
        print('   Current domains:', iterator.current_domains)
        # print('   result', result)
        iterator.mark_as_complete(result[0])
        yield result
    executor.shutdown()


if __name__ == '__main__':

    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        url_gen = (line['url'] for line in reader)

        for url, result in multithreaded(task, url_gen, WORKERS):
            print(url, '-', result)
