from pyphen import Pyphen
import string

def Syllable_Count(s_word):
	exclude = list(string.punctuation)
	s_word = s_word.lower()
	s_word = "".join(x for x in s_word if x not in exclude)

	if s_word is None:
		return 0
	elif len(s_word) == 0:
		return 0
	else:
		dic = Pyphen(lang='en_US')
		count = 0
		for word in s_word.split(' '):
			word_hyphenated = dic.inserted(word)
			count += max(1, word_hyphenated.count("-") + 1)
		return count

def changeTense(word, tense):
	fin_word = []
	vowels = ['a','e','i','o','u']
	if tense == "VBD":
		if word[len(word)-1] == 'e' and word[len(word)-2] != 'e' and word[len(word)-2] != 'y' and word[len(word)-2] != 'o':
			#print("RULE-1")
			for w in word:
				fin_word.append(w)
			rule = 'd'		
			fin_word.append(rule)
		elif word[len(word)-1] == 'e' and (word[len(word)-2] == 'e' or word[len(word)-2] == 'y' or word[len(word)-2] == 'o'):
			#print("RULE-2")
			for w in word:
				fin_word.append(w)
			rule = 'd'		
			fin_word.append(rule)
		elif word[len(word)-1] == 'l' and (word[len(word)-2] in vowels):
			#print("RULE-3")
			for w in word:
				fin_word.append(w)
			rule = 'led'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] not in vowels and (word[len(word)-2] in vowels) and (word[len(word)-3] not in vowels) and word[len(word)-1] != 'c':
			#print("RULE-4")
			for w in word:
				fin_word.append(w)
			rule = word[len(word)-1] + 'ed'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] not in vowels and (word[len(word)-2] in vowels) and (word[len(word)-3] not in vowels) and Syllable_Count(word) == 1  and word[len(word)-1] != 'c':
			#print("RULE-5")
			for w in word:
				fin_word.append(w)
			rule = word[len(word)-1] + 'ed'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] not in vowels and (word[len(word)-2] in vowels) and (word[len(word)-3] in vowels) and word[len(word)-1] != 'l':
			#print("RULE-6")
			for w in word:
				fin_word.append(w)
			rule = 'ed'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] == 'c':
			#print("RULE-7")
			for w in word:
				fin_word.append(w)
			rule = 'ked'
			for r in rule:		
				fin_word.append(r)
		else:
			#print("RULE-8")
			for w in word:
				fin_word.append(w)
			rule = 'ed'
			for r in rule:		
				fin_word.append(r)
	elif tense == "VBG":
		if word[len(word)-1] == 'e' and word[len(word)-2] != 'e' and word[len(word)-2] != 'y' and word[len(word)-2] != 'o':
			#print("RULE-1")
			for w in word:
				fin_word.append(w)
			rule = 'ing'		
			fin_word.append(rule)
		elif word[len(word)-1] == 'e' and (word[len(word)-2] == 'e' or word[len(word)-2] == 'y' or word[len(word)-2] == 'o'):
			#print("RULE-2")
			for w in word:
				fin_word.append(w)
			rule = 'ing'		
			fin_word.append(rule)
		elif word[len(word)-1] == 'l' and (word[len(word)-2] in vowels):
			#print("RULE-3")
			for w in word:
				fin_word.append(w)
			rule = 'ling'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] not in vowels and (word[len(word)-2] in vowels) and (word[len(word)-3] not in vowels) and word[len(word)-1] != 'c':
			#print("RULE-4")
			for w in word:
				fin_word.append(w)
			rule = word[len(word)-1] + 'ing'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] not in vowels and (word[len(word)-2] in vowels) and (word[len(word)-3] not in vowels) and Syllable_Count(word) == 1  and word[len(word)-1] != 'c':
			#print("RULE-5")
			for w in word:
				fin_word.append(w)
			rule = word[len(word)-1] + 'ing'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] not in vowels and (word[len(word)-2] in vowels) and (word[len(word)-3] in vowels) and word[len(word)-1] != 'l':
			#print("RULE-6")
			for w in word:
				fin_word.append(w)
			rule = 'ing'
			for r in rule:		
				fin_word.append(r)
		elif word[len(word)-1] == 'c':
			#print("RULE-7")
			for w in word:
				fin_word.append(w)
			rule = 'king'
			for r in rule:		
				fin_word.append(r)
		else:
			#print("RULE-8")
			for w in word:
				fin_word.append(w)
			rule = 'ing'
			for r in rule:		
				fin_word.append(r)
					
	f = ''													
	for letter in fin_word:
		f += letter		
	return f


if __name__ == "__main__":

	word = "vie"
	tense = "VBD"

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
			print(past_simple[word])
		else:
			print(changeTense(word, tense))
	else:
		print(changeTense(word, tense))				