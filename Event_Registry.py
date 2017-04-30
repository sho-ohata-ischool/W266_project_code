## Main python script to obtain data from Event Registry
## The Onion and The Borowitz report have to be extracted
## slightly differently due to filtering out of some of the 
## data and extraction of additional data.
## Written for python 2.7x

import json
import requests
from datetime import datetime
from datetime import timedelta
from eventregistry import *
from bs4 import BeautifulSoup

with open("credentials.txt",'r') as f:
    username, pw, apikey = f.readlines()
    username = username.split('\n'[0])
    pw = pw.split('\n'[0])

## Helper function extracted related events in Event Registry
def extract_related_articles(eventuri):
	q = QueryEvent(eventuri)
	q.addRequestedResult(RequestEventInfo())
    q.addRequestedResult(RequestEventArticles(count = 50, lang = ["eng"]))
    res_event = er.execQuery(q)

    related_articles = {}
    for x in range(res_event.values()[0]['articles']['count']):            
        article_id = res_event.values()[0]['articles']['results'][x]['id']
        if article_id != article['id']:
            article_event = res_event.values()[0]['articles']['results'][x]
            article['related_articles'][article_id] = {key: article_event[key] for key in ['date', 'title', 'url', 'body']}
        else:
            next
    return related_articles

## Helper function to query Event Registry
def query_ER(url, query_start_date, day_increment, keyword=None):
    if keyword=None:
        q = QueryArticles(dateStart = query_start_date, dateEnd = query_start_date + timedelta(days=day_increment))
    else:
        q = QueryArticles(keywords = keyword, dateStart = query_start_date, dateEnd = query_start_date + timedelta(days=day_increment))
    q.addNewsSource(url)
    q.addRequestedResult(RequestArticlesInfo(page = 1, count = 200, sortBy = "date",  sortByAsc = True,
        returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True, categories = True, image = False)
        )))
    res = er.execQuery(q) ##response is JSON
    return res

## Begin code for extracting The Onion data from Event Registry
db = {}
    
query_start_date = datetime(2013, 12, 13)
query_end_date = datetime(2017,4,1)
er = EventRegistry(apiKey = apikey)

while query_start_date <= query_end_date:
    res = query_ER('www.theonion.com', query_start_date, 15)
    
    for a in range(res['articles']['count']):
        article = res['articles']['results'][a]
        if article['id'] not in db.keys():
            
            if article['url'].split('.com/')[1].split('/')[0] == 'r': ##Some of the data stored in ER does not give the full URL
                page = requests.get(article['url']) ## scrape site data to get the correct title and url
                if page.status_code == 200:
                    soup = BeautifulSoup(page.content, 'html.parser')
                    article['url'] = soup.find("meta",  property="og:url")['content']
                    article['title'] = soup.find("meta",  property="og:title")['content']
            
            ## American Voices, videos, etc. did not have specifically humorous titles so using only sections titled articles
            if article['url'].split('.com/')[1].split('/')[0] in ['article', 'articles']:
                
                concept = {} ## Extract concepts and associated scores
                for b in range(len(res['articles']['results'][a]['concepts'])):
                     concept[article['concepts'][b]['label']['eng']] = article['concepts'][b]['score']
                
                db[article['id']] = {
                                     'title': article['title'], 
                                     'timestamp': article['dateTime'], 
                                     'concept': concept,
                                     'event': article['eventUri'],
                                     'url': article['url']
                                    }
                
                ## If there is an associated event use Event Registry to query the data
                if 'related_articles' not in article.keys() and article['eventUri'] is not None:
                    db[article['id']]['related_articles'] = extract_related_articles(article['eventUri'])
                
            else:
                next
        else:
            next
    
    query_start_date = query_start_date + timedelta(days=15)

with open("the_onion.json", "w") as f:
    json.dump(db, f, indent=2)

##For The New Yorker - Borowitz Report
query_start_date = datetime(2013, 12, 13)
query_end_date = datetime(2017,4,1)

db = {}

while query_start_date <= query_end_date:
    res = query_ER('www.theonion.com', query_start_date, 25, keyword='Borowitz Report')
     
    for a in range(res['articles']['count']):
        article = res['articles']['results'][a]
        if article['id'] not in db.keys():
            concept = {}

            for b in range(len(res['articles']['results'][a]['concepts'])):
                 concept[article['concepts'][b]['label']['eng']] = article['concepts'][b]['score']
                    
            db[article['id']] = {
                                 'title': article['title'], 
                                 'timestamp': article['dateTime'], 
                                 'concept': concept,
                                 'event': article['eventUri'],
                                 'url': article['url']
                                }
                    
            if 'related_articles' not in article.keys() and article['eventUri'] is not None:
                db[article['id']]['related_articles'] = extract_related_articles(article['eventUri'])

        else:
            next
   
    query_start_date = query_start_date + timedelta(days=25)
    
with open("borowitz_report.json", "w") as f:
    json.dump(db, f, indent=2)

## For The New York Times
db = {}
    
query_start_date = datetime(2013, 12, 13)
query_end_date = datetime(2017,4,1)

while query_start_date <= query_end_date:
    res = query_ER('www.nytimes.com', query_start_date, 1)

    for a in range(res['articles']['count']):
        article = res['articles']['results'][a]
        if article['id'] not in db.keys():
            concept = {}

            for b in range(len(res['articles']['results'][a]['concepts'])):
                 concept[article['concepts'][b]['label']['eng']] = article['concepts'][b]['score']
                    
            db[article['id']] = {
                                 'title': article['title'], 
                                 'body': article['body'],
                                 'timestamp': article['dateTime'], 
                                 'concept': concept,
                                 'event': article['eventUri'],
                                 'url': article['url']
                                }
                    
        else:
            next
    
    query_start_date = query_start_date + timedelta(days=1)

for x in list(db.keys()):
    try:
        section = db[x]['url'].split('/')[6]
        ## Remove articles from unnecessary sections
        if section in ['opinion', 'magazine', 'theater', 'crosswords', 'briefing', 'fashion', 'travel', 'realestate', 'weddings', 'pageoneplus']:
            del db[x]
    except:
        del db[x]

with open("NY_Times.json", "w") as f:
    json.dump(db, f, indent=2)