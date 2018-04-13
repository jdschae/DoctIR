from bs4 import BeautifulSoup
import time
import requests
import sys
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

BASE = 'https://www.cdc.gov'
URLS = []
SEEN = {}
QUEUE = []

#if h3.text == 'Symptoms'

def scrapePage(url, desc):
	global QUEUE
	print('@@@ ScrapePage: {}'.format(url))
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	removedOne = False
	try:
		all_tags = soup.find_all(True)
		h3s= soup.find_all('h3')
		h1 = soup.find_all('h1')
		allP = soup.find_all('p')
		printList = []
		#print h1[0].text
		if (len(h1)) and ('symptom' in h1[0].text.lower() or 'signs' in h1[0].text.lower()):
			print('h1')
			symptoms1 = h1[0].findNext('ul')
			for symp1 in symptoms1:
				printList.append('\t{}'.format(symp1))
		for h3 in h3s:
			if (('Symptoms' in h3.text) or ('symptoms' in h3.text) or ('Signs' in h3.text) or ('signs' in h3.text)):
				print('h3', h3.text)
				if('Recognize' in h3.text):
					print('Recognize break')
					break
				symptoms_list = h3.findNext('ul')
				next_para = h3.findNext('p')
				if (next_para in all_tags) and (all_tags.index(next_para) - all_tags.index(h3)) == 1:
					printList.append(next_para.text)
				else:
					print('p not right')
				tagDif = all_tags.index(symptoms_list) - all_tags.index(h3)
				if (tagDif <= 2) and (tagDif > 0):
					print(tagDif)
					symptoms = symptoms_list.find_all('li')
					for symp in symptoms:
						if ('Diagnosis' in symp.text) or ('Prevention' in symp.text) or ('diagnos' in symp.text) or ('Vaccination' in symp.text) or ("Vital Signs" in symp.text) or ("References" in symp.text):
							print('diagnosis break')
							removedOne = True
							break
						printList.append('\t{}'.format(symp.text))

				else:
					print('ul tagDif wrong')

		for para in allP:
			if ('symptom' in para.text.lower()) and (para.text[-1] == ':'):
				symptList = para.findNext('ul')
				for symp in symptList:
					printList.append('\t{}'.format(symp))

		if not removedOne:
			for string in printList:
				print(string)

		linksOnPage = soup.find_all('a', href = True)
		results = []
		numLinksSeen = 0
		for link in linksOnPage:
			# linkMod = urllib2.unquote(link['href'])
			if (('Symptoms' in link['href']) or ('symptoms' in link['href']) or ('Signs' in link['href']) or ('signs' in link['href'])) and ('vital' not in link['href']) and ('Vital' not in link['href']):
				extension = link['href']
				if '.gov' in extension:
					extension = extension.split('.gov')[1]
				next_url = BASE + extension
				if (next_url not in SEEN) and ('mp4' not in extension):
					results.append((next_url, link.text))
					SEEN[next_url] = True
					print('Page:' + next_url)
					numLinksSeen += 1
		if numLinksSeen > 0:
			QUEUE += results

	except UnicodeEncodeError:
		x = 2

def scrapeList(url):
	print('### ScrapeList: {}'.format(url))
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	section = soup.find(class_='span16')
	letters = section.find_all('a')
	results = []
	for letter in letters:
		extension = letter['href']
		#next_url = BASE + extension
		if extension not in SEEN:
			results.append((extension, letter.text))
			SEEN[extension] = True
			print('Page:' + extension)
	return results

def crawlPages(seed_url):
	global QUEUE
	# add to seen
	SEEN[seed_url] = True
	# start with index
	response = requests.get(seed_url)
	soup = BeautifulSoup(response.text, 'html.parser')
	section = soup.find(class_='az_index')
	letters = section.find_all('a')
	for letter in letters:
		extension = letter['href']
		next_url = BASE + extension
		if letter.text <= 'z' and letter.text >= 'a':
			print(next_url)
			key = 'letter' + letter.text
			if (('vital' not in next_url) and ('Vital' not in next_url)):
				QUEUE.append((next_url, key))
			else:
				for i in range(10):
					print('vital error')

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
	crawlPages('https://www.cdc.gov/diseasesconditions/index.html')
