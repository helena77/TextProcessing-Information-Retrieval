import requests
from importlib import reload

"""
This is our only interface with the SOLR service for the amzn-reviews collection
built for the first assignment.

It is simplified as follows
  * We will use only review search and ID (UUID) search
  * And within review search we will filter on score only
"""

##################################

def review_search(kw, start):
	reviews = do_query(review_query_dictionary(kw, start),"8983","amzn-reviews")
	for review in reviews['docs']:
		product = match_product(review['productID'])
		if 'productName' in product['docs'][0]:
			review.update(productName = product['docs'][0]['productName'])
		else:
			review.update(productName = "")
	return reviews

def facet_search(kw, fv, start):
	reviews = do_query(facet_query_dictionary(kw, fv, start),"8983","amzn-reviews")
	for review in reviews['docs']:
		product = match_product(review['productID'])
		if 'productName' in product['docs'][0]:
			review.update(productName = product['docs'][0]['productName'])
		else:
			review.update(productName = "")
	return reviews
	
def id_search(id):
	reviews = do_query(id_query_dictionary(id), "8983", "amzn-reviews")
	for review in reviews['docs']:
		product = match_product(review['productID'])
		if 'productName' in product['docs'][0]:
			review.update(productName = product['docs'][0]['productName'])
		else:
			review.update(productName = "")
	return reviews
	
def asin_search(id):
	return do_query(asin_query_dictionary(id),"8983","amzn-products")
	
def all_product_collection():
	return do_query(collection_all(),"8983","amzn-products")

def all_review_collection():
	return do_query(collection_all(),"8983","amzn-reviews")

def match_product(id):
	return do_query(asin_query_dictionary(id),"8983","amzn-products")

def facet(kw, start, port="8983", collection="amzn-reviews"):
	params = {"q": "_text_:" + kw, "start": start, "facet.field":"reviewScore", "facet":"on"}
	param_arg = "&".join(list(map(lambda p: f"{p[0]}={p[1]}", list(params.items()))))
	query_string = f"http://localhost:{port}/solr/{collection}/select"
	r = requests.get(query_string, param_arg)
	if (r.status_code == 200):
		scores = r.json()['facet_counts']['facet_fields']['reviewScore']
		result = []
		i = 0
		while i < len(scores):
			result.append((scores[i], scores[i + 1]))
			i = i + 2
		result.sort()
		return result
	else:
		return []

def spell_suggest(kw, start, port="8983",  collection="amzn-reviews"):
	params = {"q": "_text_:" + kw, "start": start, "spellcheck":"on"}
	param_arg = "&".join(list(map(lambda p: f"{p[0]}={p[1]}", list(params.items()))))
	query_string = f"http://localhost:{port}/solr/{collection}/spell"
	r = requests.get(query_string, param_arg)
	if (r.status_code == 200):
		suggestionsList = r.json()["spellcheck"]["collations"]
		suggestion = []
		for each in suggestionsList:
			if isinstance(each, dict):
				text, word = each["collationQuery"].split(":")
				suggestion.append(word)
		return suggestion
	else:
		raise r.raise_for_status()

def do_query(params, port, collection):
	param_arg = "&".join(list(map(lambda p: f"{p[0]}={p[1]}", list(params.items()))))
	query_string = f"http://localhost:{port}/solr/{collection}/select"
	print("Sending query " + query_string)
	print("Param " + str(params))
	r = requests.get(query_string, param_arg)
	if (r.status_code == 200):
		return r.json()['response']
	else:
		raise Exception(f"Request Error: {r.status_code}")
		
		
def id_query_dictionary(id):
	return {"q": f"id:{id}"}
	
def asin_query_dictionary(asin):
	return {"q": f"productID:{asin}"}
	
def review_query_dictionary(kw="", start=0):
	return {"q": "_text_:" + kw, "start": start}

def facet_query_dictionary(kw="",fv="", start=0):
	return {"q": "_text_:" + kw, "fq": "reviewScore:" + fv, "start": start}	

def collection_all():
	return {"q": f"*:*"}



		
