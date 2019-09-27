'''
    Web Crawler
    Script recieves the following arguments:
    - Filename to a .txt with the seed URLs to crawl from
    - maxDownloads per seed link
    - time between requests in milliseconds
    - (Optional) crawling method, depth-first (0) or breadth-first (1). Default = depth-first
'''
import sys, requests, validators, urllib
from urllib import robotparser, parse
from time import sleep
from bs4 import BeautifulSoup

def parseArgs():
    arguments = sys.argv
    if len(arguments) < 4 or len(arguments) > 5: # Arg 0 is script name
        raise TypeError("Invalid number of arguments")
    seedFilename = arguments[1]
    urlList = getURLS(seedFilename)
    maxDownloads = int(arguments[2])
    timeBetweenGETRequests = int(arguments[3])
    if len(arguments) == 5:
        if int(arguments[5]) == 0:
            depthFirst = True
        elif int(arguments[5]) == 1:
            depthFirst = False
        else:
            raise TypeError("Invalid argument for crawl method")
    else:
        depthFirst = True

    return urlList, maxDownloads, timeBetweenGETRequests, depthFirst

def getURLS(filename):
    f = open(filename)
    urlList= []
    for line in f:
        urlList.append(line)
    return urlList

def depthFirstCrawl(url, seconds):
    global downloads
    if downloads == 0:
        return

    if not validators.url(url):
        return

    if not checkRobotsForUrl(url):
        return

    r = requests.get(url)
    if "html" in r.headers["content-type"] and r.status_code == 200:
        print("Current URL: " + url)
        visitedLinks.add(url)
        html = r.text
        downloads -= 1
        sleep(seconds)
        links = parseAndFindLinks(html)

        for l in links:
            l = normalizeLink(url, l)
            if l not in visitedLinks:
                depthFirstCrawl(l, seconds)


def breadthFirstCrawl(url, seconds):
    global downloads
    queue = []
    queue.append(url)

    while queue and downloads > 0:
        currUrl = queue.pop()
        if currUrl not in visitedLinks and validators.url(currUrl) and checkRobotsForUrl(currUrl):
            print("Current URL: " + currUrl)
            visitedLinks.add(currUrl)
            r = requests.get(currUrl)
            html = r.text
            downloads -= 1
            sleep(seconds)
            links = parseAndFindLinks(html)

            for l in links:
                l = normalizeLink(url, l)
                queue.append(l)


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

def checkRobotsForUrl(url):
    global robotparser
    # Extract base URL
    parsedURL = urllib.parse.urlparse(url)
    robotsURL = parsedURL.scheme +  "://" + parsedURL.netloc + "/robots.txt"
    robotparser.set_url(robotsURL)
    robotparser.read()
    return robotparser.can_fetch("*", url)


# We parse the user-input arguments
parsedArgs = parseArgs();
urlList = parsedArgs[0]
maxDownloads = parsedArgs[1]
timeBetweenGETRequests = parsedArgs[2]
depthFirst = parsedArgs[3]

robotparser = urllib.robotparser.RobotFileParser()

visitedLinks = set()
print(checkRobotsForUrl(urlList[0]))

for url in urlList:
    downloads = maxDownloads
    if depthFirst:
        print("#### Crawling Depth First #####")
        print("Seed URL: ", url)
        depthFirstCrawl(url, timeBetweenGETRequests)
    else:
        print("#### Crawling Breadth First #####")
        print("Seed URL: ", url)
        breadthFirstCrawl(url, timeBetweenGETRequests)


