# Multithreading experiments with urls in Python.

Processing a huge amount of urls (to download the HTML, extract content, metadata...) brings two main problems: 
- Downloading articles one at a time (without multithreadng) is slow, as the cpu is idle most of the time
- If the script is multithreaded, there is the risk to make multiple requests on the same domain

This repo experiments multithreaded requests with a *no-more-than-one-or-two-requests-per-domain-at-once* rule.