from bs4 import BeautifulSoup
import time
import requests
import sys
import json
import random
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

initSymptomList = []
response = requests.get("https://healthtools.aarp.org/symptomsearch")
soup = BeautifulSoup(response.text, 'html.parser')
section = soup.find(class_='symptomseartch-tr')
symptoms = section.find_all('a')
for symp in symptoms:
    initSymptomList.append(symp.text)

#print(initSymptomList)

testList = []
for i in range(10):
    k = random.randint(1, 3)
    tempList = []
    for symptom in range(k):
        index = random.randint(0, len(initSymptomList) - 1)
        tempList.append(initSymptomList[index])
    testList.append(tempList)

print(testList)
