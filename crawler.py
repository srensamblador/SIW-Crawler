import sys, requests, urllib, validators
from time import sleep
from bs4 import BeautifulSoup

def parseArgs():
    arguments = sys.argv
    if len(arguments) !=4: # Arg 0 is script name
        raise TypeError("Expected exactly three arguments")
    seedFilename = arguments[1]
    urlList = getURLS(seedFilename)
    maxDownloads = int(arguments[2])
    timeBetweenGETRequests = int(arguments[3])
    return urlList, maxDownloads, timeBetweenGETRequests

def getURLS(filename):
    f = open(filename)
    urlList= []
    for line in f:
        urlList.append(line)
    return urlList

def crawl(url, seconds):
    global downloads
    if downloads == 0:
        return

    if not validators.url(url):
        return

    r = requests.get(url)
    if "html" in r.headers["content-type"]:
        print(".", end='')
        visitedLinks.append(url)
        html = r.text
        downloads -= 1
        sleep(seconds)
        links = parseAndFindLinks(html)

        for l in links:
            l = normalizeLink(url, l)
            if l not in visitedLinks:
                crawl(l, seconds)




def parseAndFindLinks(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.find_all("a"):
        if (link.get("href") != None):
            links.append(link.get("href"))
    return links

def normalizeLink(url, link):
    if link.startswith("/") or link.startswith("#"):
        return urllib.parse.urljoin(url, link)
    return link




# We parse the user-input arguments
parsedArgs = parseArgs();
urlList = parsedArgs[0]
maxDownloads = parsedArgs[1]
timeBetweenGETRequests = parsedArgs[2]

visitedLinks = []

for url in urlList:
    downloads = maxDownloads
    crawl(url, timeBetweenGETRequests)


