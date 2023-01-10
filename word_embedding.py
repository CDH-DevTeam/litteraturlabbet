# Python program to generate word vectors using Word2Vec

# importing all necessary modules
import json
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from spacy.lang.sv import Swedish
from gensim.models import Word2Vec

swedish_stop_words = ["aderton","adertonde","adjö","aldrig","alla","allas","allt","alltid","alltså","andra","andras","annan","annat","artonde","artonn","att","av","bakom","bara","behöva","behövas","behövde","behövt","beslut","beslutat","beslutit","bland","blev","bli","blir","blivit","bort","borta","bra","bäst","bättre","båda","bådas","dag","dagar","dagarna","dagen","de","del","delen","dem","den","denna","deras","dess","dessa","det","detta","dig","din","dina","dit","ditt","dock","dom","du","där","därför","då","e","efter","eftersom","ej","elfte","eller","elva","emot","en","enkel","enkelt","enkla","enligt","ens","er","era","ers","ert","ett","ettusen","fanns","fem","femte","femtio","femtionde","femton","femtonde","fick","fin","finnas","finns","fjorton","fjortonde","fjärde","fler","flera","flesta","fram","framför","från","fyra","fyrtio","fyrtionde","få","får","fått","följande","för","före","förlåt","förra","första","genast","genom","gick","gjorde","gjort","god","goda","godare","godast","gott","gälla","gäller","gällt","gärna","gå","går","gått","gör","göra","ha","hade","haft","han","hans","har","heller","hellre","helst","helt","henne","hennes","hit","hon","honom","hundra","hundraen","hundraett","hur","här","hög","höger","högre","högst","i","ibland","icke","idag","igen","igår","imorgon","in","inför","inga","ingen","ingenting","inget","innan","inne","inom","inte","inuti","ja","jag","jo","ju","just","jämfört","kan","kanske","knappast","kom","komma","kommer","kommit","kr","kunde","kunna","kunnat","kvar","legat","ligga","ligger","lika","likställd","likställda","lilla","lite","liten","litet","länge","längre","längst","lätt","lättare","lättast","långsam","långsammare","långsammast","långsamt","långt","låt","man","med","mej","mellan","men","mer","mera","mest","mig","min","mina","mindre","minst","mitt","mittemot","mot","mycket","många","måste","möjlig","möjligen","möjligt","möjligtvis","ned","nederst","nedersta","nedre","nej","ner","ni","nio","nionde","nittio","nittionde","nitton","nittonde","nog","noll","nr","nu","nummer","när","nästa","någon","någonting","något","några","nån","nånting","nåt","nödvändig","nödvändiga","nödvändigt","nödvändigtvis","och","också","ofta","oftast","olika","olikt","om","oss","på","rakt","redan","rätt","sa","sade","sagt","samma","sedan","senare","senast","sent","sex","sextio","sextionde","sexton","sextonde","sig","sin","sina","sist","sista","siste","sitt","sitta","sju","sjunde","sjuttio","sjuttionde","sjutton","sjuttonde","själv","sjätte","ska","skall","skulle","slutligen","små","smått","snart","som","stor","stora","stort","större","störst","säga","säger","sämre","sämst","så","sådan","sådana","sådant","ta","tack","tar","tidig","tidigare","tidigast","tidigt","till","tills","tillsammans","tio","tionde","tjugo","tjugoen","tjugoett","tjugonde","tjugotre","tjugotvå","tjungo","tolfte","tolv","tre","tredje","trettio","trettionde","tretton","trettonde","två","tvåhundra","under","upp","ur","ursäkt","ut","utan","utanför","ute","va","vad","var","vara","varför","varifrån","varit","varje","varken","vars","varsågod","vart","vem","vems","verkligen","vi","vid","vidare","viktig","viktigare","viktigast","viktigt","vilka","vilkas","vilken","vilket","vill","väl","vänster","vänstra","värre","vår","våra","vårt","än","ännu","är","även","åt","åtminstone","åtta","åttio","åttionde","åttonde","över","övermorgon","överst","övre"]

input = open('data/data_info.json') 
data = json.load(input)

def nltk_tokenization(sentences):
	data = []
	# iterate through each sentence in the file
	for i in sent_tokenize(sentences):
		temp = []
		# tokenize the sentence into words
		for j in word_tokenize(i):
			temp.append(j.lower())
		data.append(temp)

	return data


def page_cleaning(sentences):
	
	sentences = sentences.lower().strip()
	sentences = sentences.replace('\n', ' ')
	sentences = re.sub(r'[^\w\s]',' ', sentences)
	sentences = re.sub(r'\s{2,}', ' ', sentences)
	return sentences


def spacy_tokenization(sentences):
	data = []
	nlp = Swedish()
	nlp.max_length = 1500000
	doc = nlp(sentences)

	for token in doc:
		data.append(token.text)
	return data


def remove_stop_words(sentences):
	for word in sentences:
		if word in swedish_stop_words:
			sentences.remove(word)
			continue
	return sentences


def create_word_embedding(data):
	# Create CBOW model
	model = Word2Vec(data, min_count = 3,
					vector_size = 200, window = 5)

	word_vectors = model.wv

	return word_vectors


def author_per_work_vector():
	for author in data:
		author_name = author['name']
		author_id = str(author['id'])
		author_works = author['works']
		for work in author_works:
			if author_works:
				work_pages = []
				pages = work['pages']
				work_id = str(work['id'])
				work_text = ''
				if pages:
					for page in pages:
						text = page['text']
						if text != "":
							text = page_cleaning(text)
							work_text += " "+text
							tokenized_page = spacy_tokenization(text)
							tokenized_page = remove_stop_words(tokenized_page)
							work_pages.append(tokenized_page)
				if work_pages:
					work_embedding = create_word_embedding(work_pages)
					work_embedding.save(author_id+'_'+work_id+'.kv')
				


def authors_works_vector():
	for author in data:
		author_name = author['name']
		author_id = str(author['id'])
		author_works = author['works']
		all_author_works = []
		if author_works:
			for work in author_works:
				pages = work['pages']
				if pages:
					for page in pages:
						text = page['text']
						if text != "":
							tokenized_page = spacy_tokenization(text)
							tokenized_page = remove_stop_words(tokenized_page)
							all_author_works.append(tokenized_page)

			if all_author_works:
				works_embedding = create_word_embedding(all_author_works)
				works_embedding.save(author_id+'.kv')

author_per_work_vector()