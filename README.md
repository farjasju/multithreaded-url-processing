# Multithreading experiments with urls in Python.

Processing a huge amount of urls (to download the HTML, extract content, metadata...) comes with 3 main issues: 
- Downloading articles one at a time (without multithreadng) is slow, as the cpu is idle most of the time
- If the script is multithreaded, there is the risk to make multiple requests on the same domain
- If the source file listing the urls is really huge (like a 2 million entry csv), it can't be loaded in memory and has to be consumed row by row

This repo experiments multithreaded requests from a row-by-row consumed csv, with a *no-more-than-one-or-two-requests-per-domain-at-once* rule.