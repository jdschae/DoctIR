from bs4 import BeautifulSoup
import time
import requests
import sys
from string import ascii_uppercase
import json
import queue

MAYO_BASE = 'https://www.mayoclinic.org'
URLS = []
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
    for c in list(ascii_uppercase) + ['0-9']:
        print(c)
        base_url = wiki_disease_base + '_({})'.format(c)
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        #print(soup.find_all('div', id='mw-content-text', dir='ltr'))
        for child_tag in soup.find('div', class_='mw-parser-output').children:
            if child_tag.name == 'ul':
                for disease_link_tag in child_tag.find_all('a'):
                    if disease_link_tag and disease_link_tag['href']:
                        if (disease_link_tag.has_attr('title') and '(page does not exist)' in disease_link_tag['title']) \
                                or (disease_link_tag.has_attr('rel') and 'nofollow' in disease_link_tag['rel']):
                            continue
                       # print(disease_link_tag)
                        wiki_data = scrapeWiki(base, wiki_data, disease_link_tag)

                        #for tag in info_tag.find_all('ul'):

                        #wiki_data[disease_link_tag.contents[0]] = info_tag.find_all('p') + info_tag.find_all('ul')
    return wiki_data
def scrapeWiki(base, wiki_data, link):
    try:
        response = requests.get(base + link['href'])
        disease_soup = BeautifulSoup(response.text, 'html.parser')
        info_tag = disease_soup.find('div', class_='mw-parser-output')
        wiki_data[link.text] = {'text': "", 'symptoms_list': []}
        is_symptom = False
        for tag in info_tag.find_all():
            if tag.name == 'h2':
                is_symptom = 'symptoms' in tag.text.lower()

            if is_symptom:
                wiki_data[link.text]['symptoms_list'].append(tag.text)
            else:
                wiki_data[link.text]['text'] += ' ' + tag.text
    except:
        print(link['href'] + " failed")
    return wiki_data

if __name__ == '__main__':
    with open('wikipedia.txt', 'w') as outfile:
        json.dump(crawlWiki('https://en.wikipedia.org', 'https://en.wikipedia.org/wiki/List_of_diseases'), outfile)
        # crawlMayo('https://www.mayoclinic.org/diseases-conditions/index')
        # with open('mayoclinic.txt', 'w') as outfile:
        # 	json.dump(DB, outfile)