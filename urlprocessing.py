import concurrent.futures
import urllib.request
import csv
import os

WORKERS = 20
CSV_FILE = os.path.join('data', 'urls.csv')


def task(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as conn:
            data = conn.read()
        return (url, len(data))
    except:
        return (url, 'failure')


def multithreaded(task, urls, workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(task, urls):
            yield result


with open(CSV_FILE, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    url_gen = (line['url'] for line in reader)

    for url, result in multithreaded(task, url_gen, WORKERS):
        print(url, '-', result)
