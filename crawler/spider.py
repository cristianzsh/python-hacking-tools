import optparse
import requests
import re
import urlparse

target = "http://target/"
target_links = []

def extract_links(url):
    response = requests.get(url)
    return re.findall("(?:href=\")(.*?)\"", response.content)

def crawl(url):
    links = extract_links(url)
    for link in links:
        link = urlparse.urljoin(url, link)
        
        if "#" in link:
            link = link.split("#")[0]
            
        if target in link and link not in target_links:
            target_links.append(link)
            print(link)
            crawl(link)

crawl(target)
