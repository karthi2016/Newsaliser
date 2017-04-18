from flask import Flask, request, Response, abort, render_template
from flask.ext.classy import FlaskView, route
from json import dumps
import db
from scrape import merge_article


class ArticlesView(FlaskView):

	def post(self):
		url = request.get_data()
		_id = merge_article(url)
		res ={
			'result':'Success',
			'id':_id
		}
		return Response(
				response = dumps(res),
				status = 200,
				mimetype= 'application/json'
			)

	def index(self):
		arts = db.get_nodes('Article', 10, order='title')
		return render_template(
			'articles.html',
			articles=arts
			)

	def get(self, id):
		art = dict(db.get_node(id).items())
		sources = db.get_article_sources(art['url'])
		topics = db.get_article_topics(art['url'])
		art['text'] = art.get('text','') or db.get_article_text(id)
		return render_template(
			'article.html',
			sources=sources,
			nSources=len(sources),
			topics=topics,
			**art
			)



class TopicsView(FlaskView):
	def index(self):
		topics = db.get_nodes('Topic',order='name',limit=10)
		return render_template(
			'topics.html',
			topics=topics
			)

	def get(self, id):
		topic = db.get_node(id)
		articles = db.get_topic_articles(topic['name'])
		return render_template(
			'topic.html',
			articles=articles,
			**topic
			)

class DomainsView(FlaskView):
	def index(self):
		domains = db.get_nodes('Domain',order='domain',  limit=100)
		return render_template(
			'domains.html',
			domains=domains
			)

	def get(self, id):
		try:
			domain = dict(db.get_node(id).items())
		except ValueError:
			domain = dict(db.get_node_by_propval('domain',id.capitalize()))
		articles = db.get_domain_articles(domain['domain'])
		domain['nArticles'] = len(articles)
		domain['articles'] = articles
		return render_template(
			'domain.html',
			**domain
			)


app = Flask(__name__)
ArticlesView.register(app)
TopicsView.register(app)
DomainsView.register(app)

@app.errorhandler(500)
def internal_error(e):
	print e
	return Response(
		response =dumps({'error':str(e)}),
		status = 500,
		mimetype = 'application/json'
	)

if __name__ == '__main__':
	def internal_error(e):
		print e
		return Response(
			response =dumps({'error':str(e)}),
			status = 500,
			mimetype = 'application/json'
		)
	app.run(host='0.0.0.0', debug=True)