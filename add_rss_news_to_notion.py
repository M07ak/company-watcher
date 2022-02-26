from datetime import datetime
import os
from pprint import pprint
from dateutil.parser import parse
from urllib.parse import urlparse
from urllib.parse import parse_qs

import feedparser
import html2text

import notion


NOTION_SOURCE_DATABASE_PAGE_ID = os.getenv("NOTION_SOURCE_DATABASE_PAGE_ID")
NOTION_OUTPUT_FEED_PAGE_ID = os.getenv("NOTION_OUTPUT_FEED_PAGE_ID")

NOTION_OUTPUT_DB_NAME = "News"

html_parser = html2text.HTML2Text()
html_parser.unicode_snob = True
html_parser.strong_mark = ""

oldest_publication_date = datetime.utcnow()
all_notion_rss_items_by_google_tag = {}
companies = notion.get_companies_from_notion_db(NOTION_SOURCE_DATABASE_PAGE_ID)

for company in companies:
    
    try:
        name = company["properties"]["Name"]["title"][0]["plain_text"]
    except:
        continue
    

    try:
        rss_link = company["properties"]["rss"]["url"]
        news_feed  = feedparser.parse(rss_link)
    except:
        continue
    
    print(f"Found {len(news_feed.entries)} for {name}")
    
    news_to_add = []

    for entry in news_feed.entries:
        
        # if entry.id not in rss_tags_already_in_db:
        publication_date = parse(entry.published, ignoretz=True)
        if publication_date < oldest_publication_date:
            oldest_publication_date = publication_date
        
        try:
            google_url = urlparse(entry.link)
            newspapper_url = parse_qs(google_url.query)['url'][0]
            parsed_newspapper_url = urlparse(newspapper_url)
            splitted_domain = parsed_newspapper_url.hostname.split(".")
            source = f"{splitted_domain[-2]}.{splitted_domain[-1]}"
        except:
            newspapper_url = entry.link
            source = "inconnue"
        
        all_notion_rss_items_by_google_tag[entry.id] = notion.notion_prepare_rss_item(NOTION_OUTPUT_FEED_PAGE_ID, company["id"], entry.id, html_parser.handle(entry.title), html_parser.handle(entry.summary), publication_date, newspapper_url, source)


# List all tags already in Notion output DB
rss_tags_already_in_db = []
rss_output_db_content = notion.get_rss_news_from_notion_db(NOTION_OUTPUT_FEED_PAGE_ID, min_publication_date=oldest_publication_date)
for rss_content in rss_output_db_content:
    
    if rss_content["properties"]["Tag"]['rich_text']:
        rss_tags_already_in_db.append(rss_content["properties"]["Tag"]['rich_text'][0]["plain_text"])


for rss_tag_id in all_notion_rss_items_by_google_tag:
    if rss_tag_id not in rss_tags_already_in_db:
        notion.notion_post_rss_item(all_notion_rss_items_by_google_tag[rss_tag_id])
