import re
from urllib.parse import urlparse
from utils.response import Response
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse

dec_values = set()
dec_values.update(range(48,57+1))
dec_values.update(range(65,90+1))
dec_values.update(range(97,122+1))

#Allowed domains
allowed_domains = ("ics.uci.edu","cs.uci.edu","informatics.uci.edu","stat.uci.edu")    
allowed_domain2 = "https://today.uci.edu/department/information_computer_sciences"

#Read stopwords from text 
def load_stopwords():
    stop_words = set()
    f = open("stopwords.txt","r")
    words = f.read().split("\n")
    for word in words:
        stop_words.add(word)
    return stop_words
stop_words = load_stopwords()

def tokenize(html):
    html = html.split("\n")
    tokens = []
    for line in html:
        line = str(line)
        for word in re.split("[\s;,\-\n.?']",line):
            if len(word) > 1:
                word = word.lower()
                val = checkalnum(word)
                if val and word not in stop_words:
                    tokens.append(word)
    return tokens

def defragURL(url):
    url = url.split("#")
    # Doug - begin
    # if the url still has the backslash ('/') after defragging, remove it
    # used to download already downloaded links like:
    #       Initial download: https://ngs.ics.uci.edu/echronicles/
    #       Potential repeat:  https://ngs.ics.uci.edu/echronicles
    s = url[0]
    if(len(s) != 0):
        if (s[len(s)-1] == '/'):
            s = s[:len(s)-1]
            url = [s]
    # Doug - end
    return url[0]

def is_valid(url):
    try:
        parsed = urlparse(url)
        url = defragURL(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.netloc[4:] not in allowed_domains and url[:62] != allowed_domain2:
            return False
        # check for pdf, ppsx
        # examples of bad pdf linkds
        # 
        #   unusual ppsx - http://www.ics.uci.edu/~shantas/class/2019/cs122a/indexing.ppsx
        #   regular pdf link - https://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018
        #   wp-content direct pdf-link: http://emj.ics.uci.edu/wp-content/emj/uploads/MjolsnessCunhaPMAV24Oct2012
        if "pdf" in url:
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|pdf-1|odc)$", parsed.path.lower()):
            return False
        if parsed.query:
            if re.match(
                    r".*\.(css|js|bmp|gif|jpe?g|ico"
                    + r"|png|tiff?|mid|mp2|mp3|mp4"
                    + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                    + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                    + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                    + r"|epub|dll|cnf|tgz|sha1"
                    + r"|thmx|mso|arff|rtf|jar|csv"
                    + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|pdf-1|odc)$", parsed.query.lower()):
                return False
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def checkalnum(word):
    for i in range(len(word)):
        if ord(word[i]) not in dec_values:
            return False
    return True

def writeToFile(url,res):
    new_url = urlparse(url).netloc #Parse URL 
    file = open(new_url+".txt","a")
    file.write(url+"\n")
    for word in res:
        file.write(word+"\n")
    file.write("STOPHERE\n")
    file.close()
    
def scraper(url, resp):
    # Doug - move defragURL to 'is_valid' because 'is_valid' is called in frontier.py to check if
    url = defragURL(url)
    links = extract_next_links(url, resp)
    html = resp.raw_response.content

    soup = BeautifulSoup(html,'lxml')
    res = tokenize(soup.get_text())
    writeToFile(url,res)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    if is_valid(url):
        html = resp.raw_response.content

        soup = BeautifulSoup(html,'lxml')
        links = soup.find_all('a')

        res = []
        for tag in links:
            link = tag.get('href',None)
            if link is not None:
                res.append(link)
        
        return res
    # Doug added
    else:
        return([])

