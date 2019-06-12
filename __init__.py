import json, nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from flask import Flask, Response, json, jsonify, request, render_template
from py2neo import Graph, Node, Relationship #neo4j
from flask_login import LoginManager

app = Flask(__name__, static_folder='static', template_folder='static')
graph = Graph(password = "1234") #neo4j database
login = LoginManager(app) #flask login

@app.route("/", methods=["GET"])
def loginpage():
	return render_template("login.html")

@app.route("/homepage", methods=["GET"])
def homepage():
	return render_template("index.html")

#search for policies
@app.route("/search", methods=["POST"])
def search():
	try:
		stop_list = stopwords.words('english')
		stemmer = PorterStemmer()

		q = request.json['query']
		q2 = nltk.word_tokenize(q) #tokenize words
		q3 = [w.lower() for w in q2] #lowercase
		q4 = [w for w in q3 if re.search('^[a-z]+$', w)] #keep only alphabets
		q5 = [stemmer.stem(w) for w in q4] #stemming

	except KeyError:
		return []
	else:
		query = '''
		MATCH (node:Policy)
		WHERE node.name =~ {name}
		RETURN node
		'''

		querytest = '''
		MATCH (node:Policy)
		WHERE node.name =~ {name}
		RETURN node
		LIMIT 1
		'''		

		q6 = ""
		counter = 1
		for word in q5:
			q6 = q6 + word
			if counter < len(q5):
				q6 = q6 + "|"
			counter += 1
		
		#get query that is case insensitive
		results = graph.run(query, parameters={"name": "(?i).*(" + q6 + ").*"})
		resultstest = graph.run(querytest, parameters={"name": "(?i).*(" + q6 + ").*"}) #checking if there are any results

		if resultstest.evaluate(): #if there are results
			return jsonify(
				results = [{"policy": dict(row["node"])} for row in results]
			)
		else:
			return jsonify(
				results = [{"policy": {"name": "No Results Found!"}}]
			)	

#search for all related items of respective label
@app.route("/get_related/", methods=["GET"])
def get_related():
	name  = request.args.get('name')
	label  = request.args.get('label')

	query = '''
	MATCH (node:%s)-[relatedTo]-(:Policy {name: {name}}) 
	RETURN node.name as name, Type(relatedTo) as relationship, node.text as text
	''' % (label) #string formatting

	querytest = '''
	MATCH (node:%s)-[relatedTo]-(:Policy {name: {name}}) 
	RETURN node.name as name, Type(relatedTo) as relationship, node.text as text
	LIMIT 1
	''' % (label) #string formatting

	results = graph.run(query, parameters={"name": name})
	resultstest = graph.run(querytest, parameters={"name": name}) #checking if there are any results

	dictionary = {}
	textlist = []

	if resultstest.evaluate(): #if there are results
		for row in results: #change into dictionary format
			relationship = row["relationship"]
			text = row['text']
			textlist.append(text)

			if relationship in dictionary:
				dictionary[relationship] = dictionary[relationship] + ", " + row["name"]
			else:
				dictionary[relationship] = row["name"]
		return jsonify(
			results = dictionary,
			textlist = textlist
		)
	else:
		return jsonify(
			results = None
		)	

"""
@app.route("/graph", methods=["GET"])
def get_graph():
	query = '''
	MATCH (m:Movie)<-[:ACTED_IN]-(a:Person)
	RETURN m.title as movie, collect(a.name) as cast
	LIMIT {limit}
	'''

	results = graph.run(query, {"limit": 100})
	nodes = []
	rels = []

	i = 0
	for movie, cast in results:
		nodes.append({"title": movie, "label": "movie"})
		target = i
		i += 1

		for name in cast:
			actor = {"title": name, "label": "actor"}
			try:
				source = nodes.index(actor)
			except ValueError:
				nodes.append(actor)
				source = i
				i += 1
			rels.append({"source": source, "target": target})
			
	return jsonify({"nodes": nodes, "links": rels})

@app.route("/movie/<title>", methods=["GET"])
def get_movie(title):
	query = '''
	MATCH (movie:Movie {title:{title}})
	OPTIONAL MATCH (movie)<-[r]-(person:Person)
	RETURN movie.title as title,
	collect([person.name, head(split(lower(type(r)),'_')), r.roles]) as cast
	LIMIT 1
	'''

	results = graph.run(query, {"title": title})
	row = results.next()

	return jsonify({"title": row["title"],
			"cast": [dict(zip(("name", "job", "role"), member)) for member in row["cast"]]})
"""