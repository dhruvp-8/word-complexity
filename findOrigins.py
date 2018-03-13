import nltk
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup
import urllib3
import html5lib
from tqdm import tqdm

def findOrigins(word):
	urllib3.disable_warnings()
	http = urllib3.PoolManager()
	url = "http://www.dictionary.com/browse/antique"
	response = http.request('GET', url)
	soup = BeautifulSoup(response.data, "lxml")
	ety = soup.findAll("a", {"class": "language-name"})
	
	fin_ety = []
	if len(ety) != 0: 
		for i in range(len(ety)):
			fin_ety.append(ety[i].text)			
	return fin_ety

def rep(word):
	return word.replace('_',' ')


words = []
for word in wn.words():
	ts = rep(word)
	words.append(ts)

origins = set()

for i in tqdm(range(len(words)), desc = 'Progress'):
	if len(findOrigins(words[i])) != 0:
		o = findOrigins(words[i])
		for j in range(len(o)):
			origins.add(o[j])

	if i % 1000 == 0:
		with open('interim_origins.txt', 'w') as f:
			f.write(str(origins))

with open('origins.txt', 'w') as myFile:
	myFile.write(str(origins))
			