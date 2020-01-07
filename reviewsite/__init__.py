import os
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for

import reviewsite.solrinterface as solr
from reviewsite.forms import ReviewSearchForm

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	
	app.config.from_mapping(
		SECRET_KEY='dev',
	)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass
		
	@app.route('/', methods=['GET'])
	@app.route('/<name>', methods=['GET'])
	def index(name=""):
		prodCount = solr.all_product_collection()
		revCount = solr.all_review_collection()
		return render_template('index.html', templatename=name, pC=prodCount, rC=revCount)
	
	@app.route('/search',methods=['GET', 'POST'])
	def searchForm():
		form = ReviewSearchForm()
		if request.method == 'GET':
			return render_template('reviewsearch.html', form=form)
		elif not form.validate():
			return render_template('reviewsearch.html', form=form)
		else:
			return redirect(url_for('searchResults', k=form.keywords.data, start=0))
		
	@app.route('/search/results')
	def searchResults():
		k = request.args.get('k')
		fv = request.args.get('facetValue')
		start = request.args.get('start')
		reviewScores = solr.facet(k, start)	
		if fv is None or len(fv)==0:	
			res = solr.review_search(k, start)
			if res["numFound"] != 0:			
				return render_template('searchresults.html', results=res, scores=reviewScores, k=k, start=int(start))
			else:
				spellCorrection = solr.spell_suggest(k, start)
				return render_template('searchresults.html', results=res, spell=spellCorrection, k=k, start=0)	
		else:	 
			res = solr.facet_search(k, fv, start)
			newScores = []
			for each in reviewScores:
				if int(fv) == int(each[0]):					
					newScores.append(each)						
			return render_template('searchresults.html', results=res, scores=newScores, k=k, facetValue=fv, start=int(start))

	@app.route('/review/detail<id>', methods=['GET'])
	def revLookup(id):
		res = solr.id_search(id)
		if (int(res['numFound']) > 1):
			raise Exception(f"Found more than one document for ID {id}")
		iddoc = '' if int(res['numFound']) == 0 else res['docs'][0]
		return render_template('reviewdetail.html', id=id, doc=iddoc)
	
	@app.route('/product/detail<id>', methods=['GET'])
	def prodLookup(id):
		res = solr.asin_search(id)
		if (int(res['numFound']) > 1):
			raise Exception(f"Found more than one document for ID {id}")
		iddoc = '' if int(res['numFound']) == 0 else res['docs'][0]
		return render_template('productdetail.html', id=id, doc=iddoc)
	##############################
	return app
