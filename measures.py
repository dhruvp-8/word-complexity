import os
import nltk
import curses
from requests import get
import json
import urllib3
import lxml
import re
import ast
import time
import operator
import string

from multiprocessing import Process, Manager, Pool
from pyphen import Pyphen
from nltk.corpus import cmudict
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.wsd import lesk
from curses.ascii import isdigit
from wiktionaryparser import WiktionaryParser
from bs4 import BeautifulSoup
from pywsd.lesk import simple_lesk
from tensefinder import changeTense

# Decorator
def time_it(func):
	def wrapper(*args, **kwargs):
		start_time = time.time()
		r = func(*args, **kwargs)
		end_time = time.time() - start_time
		print(func.__name__ + " took " + str(end_time) + " seconds ")
		return r
	return wrapper

# Definitions
def Definition(s_word, measures, sent):
	unambiguous = removeAmbiguity(sent, s_word)
	syns = []
	syns.append(unambiguous)
	if len(syns) != 0:
		measures["concept_definition"] = syns[0].definition()
	else:
		measures["concept_definition"] = "Not Found"	

# Length of the word
def Length_of_Word(s_word, measures):
	measures["length_of_word"] = len(s_word)

# Number of syllables
def Syllable_Count(s_word, lang, measures):
	exclude = list(string.punctuation)
	s_word = s_word.lower()
	s_word = "".join(x for x in s_word if x not in exclude)

	if s_word is None:
		measures["no_of_syllables"] = 0
	elif len(s_word) == 0:
		measures["no_of_syllables"] = 0
	else:
		dic = Pyphen(lang=lang)
		count = 0
		for word in s_word.split(' '):
			word_hyphenated = dic.inserted(word)
			count += max(1, word_hyphenated.count("-") + 1)
		measures["no_of_syllables"] = count

# Etymology
def Etymology(s_word, measures):
	urllib3.disable_warnings()
	http = urllib3.PoolManager()
	url = "http://www.dictionary.com/browse/" + s_word
	response = http.request('GET', url)
	soup = BeautifulSoup(response.data, "lxml")
	ety = soup.findAll("a", {"class": "language-name"})

	if len(ety) != 0: 
		fin_ety = []
		for i in range(len(ety)):
			fin_ety.append(ety[i].text)
		measures["etymology"] = fin_ety
	else:
		measures["etymology"] = "Not Found"		


# Context
def Context(word_tokens_nl, s_word, measures, idx, main_pos):
	pred = findPrecedingWords(word_tokens_nl, s_word, idx, main_pos)
	con_d = {}
	con_l = []
	sent = ''
	print(pred)
	for i in range(0, len(pred)):
		sent += pred[i] + " "	

	url = "http://phrasefinder.io/search?corpus=eng-us&query=" + sent 
	response = get(url)
	data = response.json()
	if len(data["phrases"]) != 0:
		mc = data["phrases"][0]["mc"]
		vc = data["phrases"][0]["vc"]
		con_d["matched_count"] = mc
		con_d["volume_count"] = vc
		con_l.append(con_d)
		measures["context"] = con_l 
	else:
		measures["context"] = "Not Found"


# Familiarity
def Familiarity(s_word, measures):
	word_file = open("./data/complex_count.txt","r+")
	parse_file = word_file.read()

	word_count = {}
	word_count = ast.literal_eval(parse_file)
	word_file.close()
	if s_word in word_count.keys():
		measures["familiarity"] = word_count[s_word]
	else:
		measures["familiarity"] = 0


# Number of morphemes
def Morphemes(s_word, lang, measures):
	di = Pyphen(lang = lang)
	morphemes = []
	for pair in di.iterate(s_word):
		morphemes.append(pair)

	if len(morphemes) != 0:
		measures["morphemes"] = morphemes
		measures["morphemes_count"] = len(morphemes[0])
	else:
		measures["morphemes"] = "Not Found"
		measures["morphemes_count"] = 0	

# Tense Finder
def correctTense(s_word, tense):
	word = s_word

	text_file = open('./data/irregular_verbs_form.txt', 'r')
	lines = text_file.read()
	words = lines.split("\n")
	text_file.close()
	past_simple = {}
	past_participle = {}

	for i in range(0, len(words), 3):
		past_simple[words[i]] = words[i+1]

	for i in range(0, len(words), 3):
		past_participle[words[i]] = words[i+2]

	if tense == "VBD":
		if word in past_simple:
			return past_simple[word]
		else:
			return changeTense(word, tense)
	elif tense == "JJ" or tense == "JJR" or tense == "JJS":
		return word	
	else:
		return changeTense(word, tense)		



# Find Preceding Part of the sentence
def findPrecedingWords(word_tokens_nl, s_word, idx, main_pos):
	for i in range(0, len(word_tokens_nl)):
		if s_word == word_tokens_nl[i]:
			return word_tokens_nl[0:i+1]

	mn = word_tokens_nl[0:idx]

	# Adjust the tense of the synonym
	s_word = correctTense(s_word, main_pos)
	mn.append(s_word)
	return mn	
				

# Attach Preceding Words to Dict
def AttachPredWords(word_tokens_nl, s_word, measures):
	for i in range(0, len(word_tokens_nl)):
		if s_word == word_tokens_nl[i]:
			measures["preceding_words"] = word_tokens_nl[0:i+1]						

# Ambiguity
def removeAmbiguity(sent, s_word):
	ambiguous = s_word
	unambiguous = lesk(sent, ambiguous, 'v') 
	if unambiguous:
		return unambiguous
	else:
		unambiguous = wn.synsets(s_word)[0]
		return unambiguous		

# Find Synonyms of the Words
def findSynonyms(s_word, sent, measures, main_pos):
	syn = removeAmbiguity(sent, s_word)	
	synonyms = []
	temp = syn.name()
	root_name = temp.split(".")

	app_id = '75bf3b86'
	app_key = '2cc787678601b689054268d194d3064b'

	language = 'en'
	word_id = root_name[0]

	url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower() + '/synonyms'

	r = get(url, headers = {'app_id': app_id, 'app_key': app_key})

	if r.status_code == 200:
		data = r.json()
		#l = data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["synonyms"]

		mapper = {'VBD': 'Verb', 'VBG': 'Verb', 'JJ': 'Adjective', 'JJR': 'Adjective', 'JJS': 'Adjective'}
		checkEnt = ''
		for key, value in mapper.items():
			if key == main_pos:
				checkEnt = value
				break
		l = []
		for i in range(0, len(data["results"][0]["lexicalEntries"])):
			if data["results"][0]["lexicalEntries"][i]["lexicalCategory"] == checkEnt:
				l = data["results"][0]["lexicalEntries"][i]["entries"][0]["senses"][0]["synonyms"]
				break

		for i in l:
			synonyms.append(i["text"])
	else:	
		for l in syn.lemmas():
			synonyms.append(l.name())

	measures["synonyms"] = synonyms	


def RankEvaluationModule(measures, synonyms_measures, main_pos):

	pointsForRootWord_dict = {}
	pointsForSubWord_dict = {}

	for i in range(0, len(synonyms_measures)):

		pointsForRootWord = 0
		pointsForSubWord = 0

		# Rank For Length of Word
		if measures["length_of_word"] >= synonyms_measures[i]["length_of_word"]:
			pointsForSubWord += 1
		else:
			pointsForRootWord += 1	

		# Rank For Number of Syllable	
		if measures["no_of_syllables"] >= synonyms_measures[i]["no_of_syllables"]:
			pointsForSubWord += 1
		else:
			pointsForRootWord += 1	

		# Rank For Familiarity
		if measures["familiarity"] <= synonyms_measures[i]["familiarity"]:
			pointsForSubWord += 2
		else:
			pointsForRootWord += 2	

		# Rank For Context
		if synonyms_measures[i]["context"] != "Not Found":
			if measures["context"][0]["volume_count"] <= synonyms_measures[i]["context"][0]["volume_count"]:
				pointsForSubWord += 3
			else:
				pointsForRootWord += 3	
		else:
			pointsForRootWord += 3

		# Rank For Morphemes
		if measures["morphemes_count"] >= synonyms_measures[i]["morphemes_count"]:
			pointsForSubWord += 1
		else:
			pointsForRootWord += 1

		# Rank For Etymology
		if synonyms_measures[i]["etymology"] != "Not Found":
			flag = 0
			for x in range(0, len(synonyms_measures[i]["etymology"])):	
				if 'latin' in synonyms_measures[i]["etymology"][x].lower() or 'greek' in synonyms_measures[i]["etymology"][x].lower():
					pointsForRootWord += 2
					flag = 1
					break

			if flag == 0:
				f1 = 0
				for y in range(0, len(measures["etymology"])):
					if 'latin' in measures["etymology"][y].lower() or 'greek' in measures["etymology"][y].lower():
						pointsForSubWord += 2
						fl = 1
						break

				if fl == 0:
					pointsForSubWord += 1
					pointsForRootWord += 1				
		else:
			pointsForRootWord += 2

		pointsForSubWord_dict[synonyms_measures[i]["word"]] = pointsForSubWord
		
		mixer = measures["word"] + '_' + synonyms_measures[i]["word"]

		pointsForRootWord_dict[mixer] = pointsForRootWord

	print("\n")
	print("Synonyms Points\n")
	print(pointsForSubWord_dict)
	print("\n")
	print("Root Word Points\n")
	print(pointsForRootWord_dict)
	print("\n")
	ranked_word = max(pointsForSubWord_dict.items(), key=operator.itemgetter(1))[0]
	gr_ranked_word = correctTense(ranked_word, main_pos)

	return gr_ranked_word				


def findMeasures(s_word, word_tokens_nl, lang, sent, idx, main_pos):
				
	manager = Manager()
	measures = manager.dict()


	p1 = Process(target = Definition, args = (s_word, measures, sent))
	p2 = Process(target = Length_of_Word, args = (s_word, measures))
	p3 = Process(target = Syllable_Count, args = (s_word, lang, measures))
	p4 = Process(target = Etymology, args = (s_word, measures))
	p5 = Process(target = Context, args = (word_tokens_nl, s_word, measures, idx, main_pos))
	p6 = Process(target = Familiarity, args = (s_word, measures))
	p7 = Process(target = Morphemes, args = (s_word, lang, measures))
	p8 = Process(target = findSynonyms, args = (s_word, sent, measures, main_pos))
	p9 = Process(target = AttachPredWords, args = (word_tokens_nl, s_word, measures))

	p1.start()
	p2.start()
	p3.start()
	p4.start()
	p5.start()
	p6.start()
	p7.start()
	p8.start()
	p9.start()

	p1.join()
	p2.join()
	p3.join()
	p4.join()
	p5.join()
	p6.join()
	p7.join()
	p8.join()
	p9.join()

	# Given Word
	measures["word"] = s_word
		
	# Part of Speech
	for i in range(0, len(pos_data)):
		if pos_data[i][0] == s_word:
			measures["part_of_speech"] = pos_data[i][1]		
		
	f = json.dumps(measures.copy())

	# Convert str to dictionary
	final_measures = {}
	final_measures = ast.literal_eval(f)
	
	return final_measures				 			


def findMeasuresForSynonyms(s_word, word_tokens_nl, lang, idx, main_pos):
				
	manager = Manager()
	measures = manager.dict()


	p2 = Process(target = Length_of_Word, args = (s_word, measures))
	p3 = Process(target = Syllable_Count, args = (s_word, lang, measures))
	p4 = Process(target = Etymology, args = (s_word, measures))
	p5 = Process(target = Context, args = (word_tokens_nl, s_word, measures, idx, main_pos))
	p6 = Process(target = Familiarity, args = (s_word, measures))
	p7 = Process(target = Morphemes, args = (s_word, lang, measures))

	p2.start()
	p3.start()
	p4.start()
	p5.start()
	p6.start()
	p7.start()


	p2.join()
	p3.join()
	p4.join()
	p5.join()
	p6.join()
	p7.join()

	# Given Word
	measures["word"] = s_word
		
	# Part of Speech
	for i in range(0, len(pos_data)):
		if pos_data[i][0] == s_word:
			measures["part_of_speech"] = pos_data[i][1]		
		
	f = json.dumps(measures.copy())

	# Convert str to dictionary
	final_measures = {}
	final_measures = ast.literal_eval(f)
	
	return final_measures

if __name__ == '__main__':

	start_time = time.time()

	sent = "The cat perched on the mat"
	lang = "en_US"

	stop_words = set(stopwords.words('english'))
	word_tokens = word_tokenize(sent.lower())
	word_tokens_nl = word_tokenize(sent)
	pos_tags = nltk.pos_tag(word_tokens)

	filtered_sentence = [ w for w in word_tokens if not w in stop_words ]

	pos_data = []
	words_to_be_analyzed = []
	verbs = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ", "JJS", "JJR"]
	for i in range(0, len(filtered_sentence)):
		for j in range(0, len(pos_tags)):
			if filtered_sentence[i] == pos_tags[j][0] and pos_tags[j][1] in verbs:
				words_to_be_analyzed.append(filtered_sentence[i])
				pos_data.append((filtered_sentence[i], pos_tags[j][1]))

	if len(words_to_be_analyzed) != 0:
		s_word = words_to_be_analyzed[0]
		idx = 0
		main_pos = ''

		# For initial instance to obtain POS
		for i in range(0, len(pos_data)):
			if pos_data[i][0] == s_word:
				main_pos = pos_data[i][1]

		measures = findMeasures(s_word, word_tokens_nl, lang, sent, idx, main_pos)
		for i in range(0, len(word_tokens_nl)):
			if s_word == word_tokens_nl[i]:
				idx = i
		print(measures)		
		synonyms = measures["synonyms"]
		main_pos = measures["part_of_speech"]
		synonyms_measures = []
		for s in range(0, len(synonyms)):
			synonyms_measures.append(findMeasuresForSynonyms(synonyms[s], word_tokens_nl, lang, idx, main_pos))

		#print(synonyms_measures)
		fin_ranked_word = RankEvaluationModule(measures, synonyms_measures, main_pos)

		simplified_sentence = []
		for i in range(0, len(word_tokens_nl)):
			if i == idx:
				simplified_sentence.append(fin_ranked_word)
			else:
				simplified_sentence.append(word_tokens_nl[i])

		print(simplified_sentence)			

		
	else:
		print("Sentence cannot be simplified")

	print("Execution Time: %s seconds" %(time.time() - start_time))		


