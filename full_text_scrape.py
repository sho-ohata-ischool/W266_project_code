import json
import requests
from bs4 import BeautifulSoup
import io

## Loading article data for The Onion
with open("the_onion_modified_with_related_articles.json", "r") as f:
    onion_ER = json.load(f)

the_onion_article_text = {}

for key, value in onion_ER.items():
    count += 1
    if value['url'].split('.')[1] == 'theonion':
        response = requests.get(value['url'])
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            the_onion_article_text[key] = {}
            the_onion_article_text[key]['full_text'] = soup.findAll("div", { "class" : "content-text" })[0].text
        except:
            next
    else:
        next
        
file_name = 'theonion_fulltext.json'
with io.open(file_name, 'w', encoding='utf8') as f:
    json.dump(the_onion_article_text, f, indent=2, ensure_ascii=False)

## New Yorker Borowitz
with open("borowitz_report_with_related_articles.json", "r") as f:
    borowitz_ER = json.load(f)
    
borowtiz_report_text = {}    

for key, value in borowitz_ER.items():
    response = requests.get(value['url'])
    soup=BeautifulSoup(response.content,'lxml')
    try:
        borowtiz_report_text[key] = {}
        article = soup.findAll("div", {"class": "articleBody"})[0].text
        ## Articles start with - Borowitz Report so removing them.
        if len(article.split('Report)—')) > 1:
            article = article.split('Report)—')[1]
            borowtiz_report_text[key]['full_text'] = article
        elif len(article.split('Report) – ')) > 1:
            article = article.split('Report) – ')[1]
            borowtiz_report_text[key]['full_text'] = article
        elif len(article.split('Report) — ')) > 1:
            article = article.split('Report) — ')[1]
            borowtiz_report_text[key]['full_text'] = article
        elif len(article.split('Report)–')) > 1:
            article = article.split('Report)–')[1]
            borowtiz_report_text[key]['full_text'] = article
        else:
            next
    except:
        next

with io.open('borowitz_full_text.json', 'w', encoding='utf8') as f:
    json.dump(borowtiz_report_text, f, indent=2, ensure_ascii=False)

## The New York Times
with open("NY_Times.json", "r") as f:
    nytimes_ER = json.load(f)

file_name = 'nytimes_fulltext.json'

for key, value in nytimes_ER.items():
    
    if os.path.exists(file_name):
        with open(file_name, "r", encoding='utf8') as f:
            ny_times_article_text = json.load(f)
    else:
        ny_times_article_text = {}

    if key not in list(ny_times_article_text.keys()):
        ## Remove articles from unnecessary sections
        if value['url'].split('/')[6] not in ['opinion', 'magazine', 'theater', 'crosswords', 'briefing', 'fashion', 'travel', 'realestate', 'weddings', 'pageoneplus']:
            try:
                response = requests.get(value['url'])
                soup = BeautifulSoup(response.content, 'lxml')
                article_bs4 = soup.findAll("p", {"class": "story-body-text story-content"})
                
                ny_times_article_text[key] = {}
                full_text = ''                
                for text in article_bs4: ## Articles are split up so combine all article text
                    full_text += text.text
                ny_times_article_text[key]['full_text'] = full_text

            except:
                next
        else:
            next
        
with io.open(file_name, 'w', encoding='utf8') as f:
    json.dump(ny_times_article_text, f, indent=2, ensure_ascii=False)