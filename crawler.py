from bs4 import BeautifulSoup
import time	
import requests
import sys
import json

BASE = 'https://www.mayoclinic.org'
URLS = []
SEEN = {}
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
		next_url = BASE + extension
		if '(See:' not in letter.text and next_url not in SEEN:
			SEEN[next_url] = True
			results.append((next_url, letter.text))
			print('Page:' + next_url)
	return results

def crawlPages(seed_url):
	# add to seen 
	QUEUE = []
	SEEN[seed_url] = True
	# hard code ignore
	SEEN['https://www.mayoclinic.org#index'] = True
	# start with index
	response = requests.get(seed_url)
	soup = BeautifulSoup(response.text, 'html.parser')
	section = soup.find(class_='alpha')
	letters = section.find_all('a')
	for letter in letters:
		extension = letter['href']
		next_url = BASE + extension
		if letter.text <= 'Z' and letter.text >= 'A':
			key = 'letter' + letter.text
			QUEUE.append((next_url, key))
	# start crawling]
	print('Crawling...')
	while len(QUEUE):
		current_url, t = QUEUE[0]
		QUEUE = QUEUE[1:]
		# get list page
		if 'letter' in t:
			results = scrapeList(current_url) 
			QUEUE += results
			print('$$$ {} : {}'.format(current_url, results))
		# get specific page
		else:
			scrapePage(current_url, t)

if __name__ == '__main__':
	# scrapePage('https://www.mayoclinic.org/diseases-conditions/baby-acne/symptoms-causes/syc-20369880', 'Baby Acne')
	crawlPages('https://www.mayoclinic.org/diseases-conditions/index')
	with open('mayoclinic.txt', 'w') as outfile:
		json.dump(DB, outfile)
	