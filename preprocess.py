# Alexander Li
# alexlive
from nltk.stem.porter import *
import string
import nltk
import sys
import string
import glob
import os

STOPWORDS = set()

# load stopwords
def loadStopwords():
	file_obj = open('stopwords', 'r')
	lines = file_obj.readlines()
	for line in lines:
		STOPWORDS.add(line.strip())
	file_obj.close()

# tokenize text
def tokenizeText(text):
	return nltk.word_tokenize(text)

# convert list to freq dict
def dictify(tokens, dic = {}):
	for t in tokens:
		if t not in dic:
			dic[t] = 0
		dic[t] += 1
	return dic[t]

# remove stopwords
def removeStopwords(data):
	return [i for i in data if i not in STOPWORDS]

# stem words
def stemWords(tokens):
	inst = PorterStemmer()
	result = []
	for t in tokens:
		result.append(inst.stem(t))
	return result

def preprocess(text, ngram=1):
	loadStopwords()
	translator = str.maketrans('', '', string.punctuation)
	data = text.lower().strip().translate(translator)
	# tokenize
	tokens = tokenizeText(data)
	# filter out stopwords
	filtered = removeStopwords(tokens)
	# stem tokens
	stemmed = stemWords(filtered)
	results = []
	for i in range(ngram, len(stemmed)):
		results.append(' '.join(stemmed[i-ngram:i]))
	return results

if __name__ == '__main__':
	main()
