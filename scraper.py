from bs4 import BeautifulSoup
import requests
from string import ascii_uppercase
import json
import queue
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

MAYO_BASE = 'https://www.mayoclinic.org'
SEEN = set()
DB = {}


def scrapePage(url, desc):
    print('@@@ ScrapePage: {}'.format(url))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # h2s= soup.find_all('h2')
    content = soup.find('div', class_="content")
    h2s= content.find_all('h2')
    for h2 in h2s:
        if h2.text == 'Symptoms':
            next_el = h2.findNext('p')
            DB[desc] = {}
            DB[desc]['text'] = ''
            while next_el != None and next_el.text[-1] != ':' :
                DB[desc]['text'] += next_el.text
                print(next_el.text)
                next_el = next_el.find_next_sibling('p')
            DB[desc]['symptoms_list'] = []
            if next_el == None:
                return
            symptoms_list = next_el.findNext('ul')
            symptoms = symptoms_list.find_all('li')
            for symp in symptoms:
                DB[desc]['symptoms_list'].append(symp.text)
                print('\t{}'.format(symp.text))


def scrapeList(url):
    print('### ScrapeList: {}'.format(url))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    section = soup.find(class_='index')
    letters = section.find_all('a')
    results = []
    for letter in letters:
        extension = letter['href']
        next_url = MAYO_BASE + extension
        if '(See:' not in letter.text and next_url not in SEEN:
            SEEN.add(next_url)
            results.append((next_url, letter.text))
            print('Page:' + next_url)
    return results


def crawlMayo(seed_url):
    # add to seen
    QUEUE = queue.Queue()
    SEEN.add(seed_url)
    # hard code ignore
    SEEN.add('https://www.mayoclinic.org#index')
    # start with index
    response = requests.get(seed_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    section = soup.find(class_='alpha')
    letters = section.find_all('a')
    for letter in letters:
        extension = letter['href']
        next_url = MAYO_BASE + extension
        if letter.text <= 'Z' and letter.text >= 'A':
            key = 'letter' + letter.text
            QUEUE.put((next_url, key))
    # start crawling]
    print('Crawling...')
    while not QUEUE.empty():
        current_url, t = QUEUE.get()
        # get list page
        if 'letter' in t:
            sl = scrapeList(current_url)
            for el in sl:
                QUEUE.put(el)
        # get specific page
        else:
            scrapePage(current_url, t)


def crawlWiki(base, wiki_disease_base):
    wiki_data = {}
    # For each list of diseases
    for c in list(ascii_uppercase) + ['0-9']:
        base_url = wiki_disease_base + '_({})'.format(c)
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # For each info tag
        for child_tag in soup.find('div', class_='mw-parser-output').children:
            if child_tag.name == 'ul':

                # For each disease
                for disease_link_tag in child_tag.find_all('a'):
                    if disease_link_tag and disease_link_tag['href']:
                        # Continue if page not created yet
                        if (disease_link_tag.has_attr('title') and '(page does not exist)' in disease_link_tag['title']) \
                                or (disease_link_tag.has_attr('rel') and 'nofollow' in disease_link_tag['rel']):
                            continue

                        # Scrape page
                        wiki_data = scrapeWiki(base, wiki_data, disease_link_tag)
    return wiki_data


def scrapeWiki(base, wiki_data, link):
    # If can't access page, skip
    try:
        response = requests.get(base + link['href'])
        disease_soup = BeautifulSoup(response.text, 'html.parser')
        info_tag = disease_soup.find('div', class_='mw-parser-output')

        wiki_data[link.text] = {'text': "", 'symptoms_list': []}
        is_symptom = False

        # For each child tag
        for tag in info_tag.find_all(recursive=False):
            # If symptoms section
            if tag.name == 'h2':
                is_symptom = 'symptoms' in tag.text.lower()

            # Put info as either text or symptom
            if is_symptom:
                wiki_data[link.text]['symptoms_list'].append(tag.text)
            elif tag.name == 'ul' or tag.name == 'p':
                wiki_data[link.text]['text'] += ' ' + tag.text
    except:
        print(link['href'] + " failed")

    return wiki_data


BASECDC = 'https://www.cdc.gov'
URLSCDC = []
SEENCDC = {}
QUEUECDC = []
DBCDC = {}

#if h3.text == 'Symptoms'


def scrapePageCDC(url, desc):
    global QUEUECDC
    print('@@@ ScrapePage: {}'.format(url))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    removedOne = False
    addedOne = False
    try:
        all_tags = soup.find_all(True)
        h3s= soup.find_all('h3')
        allP = soup.find_all('p')
        # printList = []
        ##print h1[0].text
        for h3 in h3s:
            if desc not in DBCDC:
                DBCDC[desc] = {}
                DBCDC[desc]['text'] = ""
                DBCDC[desc]['symptoms_list'] = []
            if (('Symptoms' in h3.text) or ('symptoms' in h3.text) or ('Signs' in h3.text) or ('signs' in h3.text)):
                #print('h3', h3.text)
                if('Recognize' in h3.text):
                    #print('Recognize break')
                    break
                symptoms_list = h3.findNext('ul')
                next_para = h3.findNext('p')
                if (next_para in all_tags) and (all_tags.index(next_para) - all_tags.index(h3)) == 1:
                    if 'brochure' not in next_para.text:
                        if len(DBCDC[desc]['text']) == 0:
                            DBCDC[desc]['text'] = next_para.text
                # else:
                #     print('p not right')
                tagDif = all_tags.index(symptoms_list) - all_tags.index(h3)
                if (tagDif <= 2) and (tagDif > 0):
                    #print(tagDif)
                    symptoms = symptoms_list.find_all('li')
                    toAppend = []
                    for symp in symptoms:
                        if (('Diagnosis' in symp.text) or ('Prevention' in symp.text) or ('diagnos' in symp.text) or ('Vaccination' in symp.text) or ("Vital Signs" in symp.text) or ("References" in symp.text)):
                            #print('diagnosis break')
                            removedOne = True
                            break
                        toAppend.append(symp.text)
                    for word in toAppend:
                        if word not in DBCDC[desc]['symptoms_list']:
                            DBCDC[desc]['symptoms_list'].append(word)
                    addedOne = True

                # else:
                #     print('ul tagDif wrong')

        for para in allP:
            if ('symptom' in para.text.lower()) and (para.text[-1] == ':'):
                symptList = para.findNext('ul')
                if (symptList in all_tags) and (all_tags.index(symptList) - all_tags.index(para) == 1):
                    if desc not in DBCDC:
                        DBCDC[desc] = {}
                        DBCDC[desc]['text'] = []
                        DBCDC[desc]['symptoms_list'] = []
                    addedOne = True
                    eachSymp = symptList.find_all('li')
                    for symp in eachSymp:
                        if symp not in DBCDC[desc]['symptoms_list']:
                            DBCDC[desc]['symptoms_list'].append(symp.text)

        # if (not removedOne) and addedOne:
        #     # DBCDC[desc]['text'].append(printList)
        #     print(desc, DBCDC[desc]['text'])
        linksOnPage = soup.find_all('a', href = True)
        results = []
        numLinksSEENCDC = 0
        for link in linksOnPage:
            # linkMod = urllib2.unquote(link['href'])
            if (('Symptoms' in link['href']) or ('symptoms' in link['href']) or ('Signs' in link['href']) or ('signs' in link['href'])) and ('vital' not in link['href']) and ('Vital' not in link['href']):
                extension = link['href']
                if '.gov' in extension:
                    extension = extension.split('.gov')[1]
                next_url = BASECDC + extension
                if (next_url not in SEENCDC) and ('mp4' not in extension):
                    results.append((next_url, desc))
                    SEENCDC[next_url] = True
                    #print('Page:' + next_url)
                    numLinksSEENCDC += 1
        if numLinksSEENCDC > 0:
            QUEUECDC += results

    except UnicodeEncodeError:
        x = 2


def scrapeListCDC(url):
    #print('### ScrapeList: {}'.format(url))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    section = soup.find(class_='span16')
    letters = section.find_all('a')
    results = []
    for letter in letters:
        extension = letter['href']
        #next_url = BASECDC + extension
        if extension not in SEENCDC:
            results.append((extension, letter.text))
            SEENCDC[extension] = True
            #print('Page:' + extension)
    return results


def crawlPagesCDC(seed_url):
    global QUEUECDC
    # add to SEENCDC
    SEENCDC[seed_url] = True
    # start with index
    response = requests.get(seed_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    section = soup.find(class_='az_index')
    letters = section.find_all('a')
    for letter in letters:
        extension = letter['href']
        next_url = BASECDC + extension
        if letter.text <= 'z' and letter.text >= 'a':
            #print(next_url)
            key = 'letter' + letter.text
            if (('vital' not in next_url) and ('Vital' not in next_url)):
                QUEUECDC.append((next_url, key))
            else:
                for i in range(10):
                    print('vital error')

    # start crawling]
    print('Crawling...')
    while len(QUEUECDC):
        current_url, t = QUEUECDC[0]
        QUEUECDC = QUEUECDC[1:]
        # get list page
        if 'letter' in t:
            QUEUECDC += scrapeListCDC(current_url)
        # get specific page
        else:
            scrapePageCDC(current_url, t)


if __name__ == '__main__':
    # Scraping each source and dumping into JSON
    with open('cdc.json', 'w') as outfile:
        crawlPagesCDC('https://www.cdc.gov/diseasesconditions/index.html')
        copyDict = DBCDC.copy()
        for illness in copyDict:
            if (DBCDC[illness]['text'] == "") and (len(DBCDC[illness]['symptoms_list']) == 0):
                DBCDC.pop(illness)
        DBCDC.pop("Yellow Fever")
        json.dump(DBCDC, outfile)
    with open('mayoclinic.json', 'w') as outfile:
        crawlMayo('https://www.mayoclinic.org/diseases-conditions/index')
        json.dump(DB, outfile)
    with open('wikipedia.json', 'w') as outfile:
        json.dump(crawlWiki('https://en.wikipedia.org', 'https://en.wikipedia.org/wiki/List_of_diseases'), outfile)
