from bs4 import BeautifulSoup
import time	
import requests
import sys

BASE = 'https://www.mayoclinic.org'
URLS = []
SEEN = {}

def scrapePage(url, desc):
	print('@@@ ScrapePage: {}'.format(url))
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	h2s= soup.find_all('h2')
	for h2 in h2s:
		if h2.text == 'Symptoms':
			next_el = h2.findNext('p')
			while next_el.text[-1] != ':':
				print(next_el.text)
				next_el = next_el.findNext('p')
			symptoms_list = next_el.findNext('ul')
			symptoms = symptoms_list.find_all('li')
			for symp in symptoms:
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
		if next_url not in SEEN:
			results.append((next_url, letter.text))
			SEEN[next_url] = True
			print('Page:' + next_url)
	return results

def crawlPages(seed_url):
	# add to seen 
	QUEUE = []
	SEEN[seed_url] = True
	# start with index
	response = requests.get(seed_url)
	soup = BeautifulSoup(response.text, 'html.parser')
	section = soup.find(class_='alpha')
	letters = section.find_all('a')
	for letter in letters:
		extension = letter['href']
		next_url = BASE + extension
		if letter.text <= 'Z' and letter.text >= 'A':
			print(next_url)
			key = 'letter' + letter.text
			QUEUE.append((next_url, key))
	# start crawling]
	print('Crawling...')
	while len(QUEUE):
		current_url, t = QUEUE[0]
		QUEUE = QUEUE[1:]
		# get list page
		if 'letter' in t:
			QUEUE += scrapeList(current_url)
		# get specific page
		else:
			scrapePage(current_url, t)

if __name__ == '__main__':
	crawlPages('https://www.mayoclinic.org/diseases-conditions/index')
