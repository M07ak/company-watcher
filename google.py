from google_alerts import GoogleAlerts
import os, pprint, time, random

import urllib.parse

GOOGLE_NEWS_MAX_SIZE = 12

# https://github.com/9b/google-alerts
use_cache = False

global ga

ga = False

# ga.create("Copeeks", {'delivery': 'RSS', 'frequency': 'realtime', 'language': 'fr', "region": "FR"})

class Term:
    def __init__(self, name, lang="fr", region="FR", rss_url="", match_type="ALL", is_tracked=False, category="Aucune"):
        self.name = name
        self.lang = lang
        self.region = region
        self.rss_url = rss_url
        self.match_type = match_type
        self.is_tracked = is_tracked
        self.category = category

        self.tracking_name = name

        if " " in name and "\"" not in name:
            self.tracking_name = f'"{name}"'

def random_wait():
    time.sleep(random.random()*10+3)

def geneate_google_news_search_urls(keywords, time_range="7d", lang="fr"):
    urls = []

    parsed_keywords = []
    for i in range(len(keywords)):
        parsed_keywords.append(f'"{keywords[i]}"')
        if len(parsed_keywords) == GOOGLE_NEWS_MAX_SIZE:
            plain_keywords = ' OR '.join(
                parsed_keywords) + " when:" + time_range
            params = urllib.parse.quote_plus(f"{plain_keywords}")
            url = f"https://news.google.com/search?q={params}"
            urls.append(url)
            parsed_keywords = []

    if len(parsed_keywords) > 0:
        plain_keywords = ' OR '.join(parsed_keywords) + " when:" + time_range
        params = urllib.parse.quote_plus(f"{plain_keywords}")
        url = f"https://news.google.com/search?q={params}"
        urls.append(url)

    return urls

def get_google_alert_conn():
    global ga
    if not ga:
        ga = GoogleAlerts(os.getenv("GOOGLE_EMAIL"), os.getenv("GOOGLE_PASSWORD"))

        ga.authenticate()
        random_wait()
    
    return ga

def get_activ_alerts():
    if use_cache:
        print("use cache")
        return [{'monitor_id': '81ffd481a5247748:0eb62326811e39c2:com:fr:FR', 'user_id': '16312343590097909905', 'term': 'Copeeks', 'language': 'fr', 'region': 'FR', 'delivery': 'RSS', 'match_type': 'ALL', 'rss_link': 'https://google.com/alerts/feeds/16312343590097909905/18263642973138901855'}, {'monitor_id': '81ffd481a5247748:6a50637476201382:com:en:US', 'user_id': '16312343590097909905', 'term': 'Environnement', 'language': 'en', 'region': 'US', 'delivery': 'RSS', 'match_type': 'ALL', 'rss_link': 'https://google.com/alerts/feeds/16312343590097909905/16902486936570905814'}, {'monitor_id': '81ffd481a5247748:7596f1dadddfbcc4:com:en:US:L', 'user_id': '16312343590097909905', 'term': 'Test', 'language': 'en', 'region': 'US', 'delivery': 'RSS', 'match_type': 'BEST', 'rss_link': 'https://google.com/alerts/feeds/16312343590097909905/11999839392461670649'}, {'monitor_id': '81ffd481a5247748:9e388fd373542e97:com:fr:FR:R', 'user_id': '16312343590097909905', 'term': 'test2', 'language': 'fr', 'region': 'FR', 'delivery': 'RSS', 'match_type': 'ALL', 'rss_link': 'https://google.com/alerts/feeds/16312343590097909905/7248440765111052270'}]
    
    alerts = get_google_alert_conn().list()
    random_wait()
    return alerts

def track_term(term):
    if not use_cache:
        # print({"name": term.tracking_name, "settings": {'delivery': 'RSS', 'frequency': 'realtime', 'language': term.lang, "region": term.region, "match_type": term.match_type}})
        # exit()
        response = get_google_alert_conn().create(term.tracking_name, {'delivery': 'RSS', 'frequency': 'realtime', 'language': term.lang, "region": term.region, "match_type": term.match_type})
        random_wait()
    
    term.rss_url = response[0]['rss_link']
    term.is_tracked = True

    print(f"Start tracking {term.name} {term.lang} {term.region}")
    return term

def untrack_term(alert):
    if not use_cache:
        get_google_alert_conn().delete(alert["monitor_id"])
        random_wait()

    print(f"Stop tracking {alert['term']} {alert['language']} {alert['region']}")

def track_terms(terms):
    activ_alerts = get_activ_alerts()
    pprint.pprint(activ_alerts)
    for term in terms:
        is_tracked = False
        for alert in activ_alerts:
            if term.tracking_name == alert["term"] and term.lang == alert["language"] and term.region == alert["region"] and term.match_type == alert["match_type"]:
                is_tracked = True
                term.is_tracked = True
                term.rss_url = alert["rss_link"]
                break
        
        if not is_tracked:
            term = track_term(term)

    for alert in activ_alerts:
        delete_required = True
        for term in terms:
            if term.tracking_name == alert["term"] and term.lang == alert["language"] and term.region == alert["region"]:
                delete_required = False
                break
        
        if delete_required:
            untrack_term(alert)
    
    return terms


if __name__ == "__main__":
    terms_to_track=[Term(name="Facebook"), Term(name="Port du Havre")]

    terms_to_track = track_terms(terms_to_track)

    for term in terms_to_track:
        print(term.rss_url)