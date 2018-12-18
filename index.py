import re
import json
import math
from bs4 import BeautifulSoup
from pymongo import MongoClient
from nltk.corpus import stopwords
from collections import defaultdict
from pymongo.errors import ConnectionFailure

class InvertedIndex:
	def __init__(self):
		self.client = MongoClient(serverSelectionTimeoutMS = 1000)

		try:
			self.client.admin.command('ismaster')
			print('Connected successfully!')

			self.database = self.client.searchEngine

			with open("WEBPAGES_RAW/bookkeeping.json") as json_file:
				self.json_data = json.load(json_file)

			self.index = defaultdict(dict)
			self.tf_idf = defaultdict(dict)

		except ConnectionFailure:
			print('Unsuccessful connection')
			exit()


	def create_index(self):
		count = 0
		for k in self.json_data.keys():
			count += 1
			if count not in [1577, 10799, 16806]:
				file = "WEBPAGES_RAW/" + str(k)
				f = open(file)
				soup = BeautifulSoup(f, "lxml")
				for script in soup(["script", "style"]):
					script.extract()

				text = soup.get_text()

				self.create_entry(text, str(k))
				print(count)
				print("\n\t" + k)


	def create_entry(self, text, doc_id):
		word_dict = defaultdict(int)

		tokens = re.split("[^A-Za-z0-9]+", text.lower())

		for word in tokens:
			if (len(word) != 0) and (word not in stopwords.words("english")):
				word_dict[word] += 1

		for token in word_dict:
			self.index[token][doc_id] = word_dict[token]


	def compute_TfIdf(self):
		N = len(self.json_data)

		for token, docs in self.index.items():
			df = len(docs)
			idf = math.log10(N / float(df))

			for doc, tf in docs.items():
				if tf > 0:
					self.tf_idf[token][doc] = (1 + math.log10(tf)) * idf
				else:
					self.tf_idf[token][doc] = 0


	def storeInDB(self):
		for token, docs in self.tf_idf.items():
			post = {token: docs}
			self.database.Table.insert_one(post)


	def lookup_index(self, query):
		''' To work with the GUI, this should return a list of relevant links
		in this format:

		[(url1, title1), (url2, title2), ...] '''

		terms = re.split("[^A-Za-z0-9]+", query.lower())

		query_scores = defaultdict(float)
		docs_intersection = []

		for term in terms:
			result = self.database.Table.find_one({term: {'$exists': True}})

			if result != None:
				docs_intersection.append(set(result[term].keys()))
				for doc, score in result[term].items():
				 	query_scores[doc] += score

		if len(docs_intersection) > 1:
			docs_intersection = set.intersection(*docs_intersection) # gets all the docs that have each term
		else:
			docs_intersection = docs_intersection[0]

		related_docs = defaultdict(float)
		for doc in docs_intersection:
			related_docs[doc] = query_scores[doc]

		links = []
		count = 0
		for doc, score in sorted(related_docs.items(), key = lambda x: (-x[1], x[0])):
			count += 1

			# using bs4 get what's in the <title> tags to display in GUI
			file = "WEBPAGES_RAW/" + str(doc)
			f = open(file)
			soup = BeautifulSoup(f, "lxml")

			for script in soup(["script", "style"]):
				script.extract()

			text = soup.get_text().split()
			if len(text) > 50:
				snippet = " ".join(text[0:15]) + "..."
			else:
				snippet = " ".join(text)
			
			if soup.find('title') != None:
				links.append((self.json_data[doc], soup.find('title').string, snippet))
			else:
				links.append((self.json_data[doc], "", snippet))

			print(self.json_data[doc] + " | score: " + str(score))

			if count == 10:
				break

		return links


	def cosine_similarity(self, query):
		word_dict = defaultdict(int)
		pl_dict = defaultdict(list)

		scores = defaultdict(float)
		length = defaultdict(float)

		N = 0

		tokens = re.split("[^A-Za-z0-9]+", query.lower())

		for word in tokens:
			if (len(word) != 0) and (word not in stopwords.words("english")):
				word_dict[word] += 1
				pl_dict[word] = self.lookup_index(word)

		for v in pl_dict.values():
			N += len(v)

		for token in word_dict:
			pl_token = pl_dict[token]
			weight_tq = (1 + math.log10(word_dict[token])) * (math.log10(N / float(len(pl_token))))
			result = self.database.Table.find_one({token: {'$exists': True}})
			result = result[token]
			for doc, score in result.items():
				weight_td = score
				scores[doc] += (weight_td * weight_tq)
				length[doc] += weight_td ** 2

		for doc in scores:
			scores[doc] = scores[doc] / math.sqrt(length[doc])

		count = 0
		for doc, score in sorted(scores.items(), key = lambda x: (-x[1], x[0])):
			count += 1
			# print(self.json_data[doc] + " " + str(score))

			if count == 10:
				break


	def close_connection(self):
		self.client.close()
		print("Connection closed!")




