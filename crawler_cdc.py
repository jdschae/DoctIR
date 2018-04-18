from bs4 import BeautifulSoup
import time
import requests
import sys
import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

BASECDCCDC = 'https://www.cdc.gov'
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
                next_url = BASECDCCDC + extension
                if (next_url not in SEENCDC) and ('mp4' not in extension):
                    results.append((next_url, desc))
                    SEENCDC[next_url] = True
                    #print('Page:' + next_url)
                    numLinksSEENCDC += 1
        if numLinksSEENCDC > 0:
            QUEUECDC += results

        # if (DBCDC[desc]['text'] == "") and (len(DBCDC[desc]['symptoms_list']) == 0):
        #     DBCDC.pop(desc)

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
    crawlPagesCDC('https://www.cdc.gov/diseasesconditions/index.html')
    copyDict = DBCDC.copy()
    for illness in copyDict:
        if (DBCDC[illness]['text'] == "") and (len(DBCDC[illness]['symptoms_list']) == 0):
            DBCDC.pop(illness)
    DBCDC.pop("Yellow Fever")
    print(DBCDC)
    print('length of DBCDC: ', len(DBCDC))
    with open('cdc.txt', 'w') as outfile:
        json.dump(DBCDC, outfile)
