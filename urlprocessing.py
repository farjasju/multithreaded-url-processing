import concurrent.futures
import urllib.request
from urllib.parse import urlparse
import time
import csv
import os
from collections import Counter
from lazypool import LazyThreadPoolExecutor
from ural import ensure_protocol


WORKERS = 20
CSV_FILE = os.path.join('data', 'source_urls.csv')

MAX_CONCURRENT_REQUESTS_BY_DOMAIN = 2


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
        self.current_domains = Counter()
        self.buffer = dict()

    def __iter__(self):
        return self

    def mark_as_complete(self, url):
        print('   REMOVING', domain_from_url(url), 'from current_domains')
        # print('   ITERATOR : MARK AS COMPLETE', url[:30])
        if self.current_domains[domain_from_url(url)] > 1:
            self.current_domains[domain_from_url(url)] -= 1
        elif self.current_domains[domain_from_url(url)] == 1:
            del self.current_domains[domain_from_url(url)]
        else:
            print("ERROR:", "Removing a domain with a count of 0")

    def __next__(self):
        url = next(self.urls)
        domain = domain_from_url(url)
        if self.current_domains[domain] >= MAX_CONCURRENT_REQUESTS_BY_DOMAIN:
            self.buffer[domain].append(url)
            print("ADDING", domain_from_url(url), "to buffer")
        else:
            self.current_domains[domain] += 1
        # print('ADDING', domain_from_url(url), 'to current_domains')
        return url


def task(url):
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

    nb_urls_processed = 0

    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        url_gen = (line['url'] for line in reader)

        for url, result in multithreaded(task, url_gen, WORKERS):
            nb_urls_processed += 1
            print('>>>', nb_urls_processed, '-', url, '-', result, '\n')
