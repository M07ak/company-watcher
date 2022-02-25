from datetime import datetime
import os
from pprint import pprint
from dateutil.parser import parse

import feedparser
import html2text

import notion


NOTION_SOURCE_DATABASE_PAGE_ID = os.getenv("NOTION_SOURCE_DATABASE_PAGE_ID")

NOTION_OUTPUT_DB_NAME = "News"

news_feed  = feedparser.parse("https://www.google.com/alerts/feeds/16312343590097909905/430879523615656862")

companies = notion.get_companies_from_notion_db(NOTION_SOURCE_DATABASE_PAGE_ID)

for company in companies:
    try:
        name = company["properties"]["Name"]["title"][0]["plain_text"]
    except:
        continue
    
    if name != "Facebook":
        continue

    try:
        rss_link = company["properties"]["rss"]["url"]
        news_feed  = feedparser.parse(rss_link)
    except:
        continue


    company_page_content = notion.get_page_content(company["id"])
    rss_output_db_id = False
    for content in company_page_content:
        if content["type"] == "child_database" and content["child_database"]["title"] == NOTION_OUTPUT_DB_NAME:
            rss_output_db_id = content["id"]

    if not rss_output_db_id:
        # Create notion inline db
        pass
    
    rss_tags_already_in_db = []
    rss_output_db_content = notion.get_rss_news_from_notion_db(rss_output_db_id)
    for rss_content in rss_output_db_content:
        if rss_content["properties"]["Tag"]['rich_text']:
            rss_tags_already_in_db.append(rss_content["properties"]["Tag"]['rich_text'][0]["plain_text"])
    
    news_to_add = []

    for entry in news_feed.entries:
        if entry.id not in rss_tags_already_in_db:
            publication_date = parse(entry.published)
            notion.notion_create_rss_item(rss_output_db_id, entry.id, html2text.html2text(entry.title), html2text.html2text(entry.summary), publication_date, entry.link)
            # exit()
            # news_to_add.append()
            # print(f"{entry.title} --> {entry.link}")
            # print(f"{entry.id}")
        else:
            # TODO: Create table
            pass
            # print(f"Don't add {entry}")

        # if news_to_add:
        #     for news in news_to_add:
        #         notion.notion_add_blocks(company["id"], [news])
        # pprint(news_to_add)

        # pprint(company)

exit()

# # Propriétés du flux
# print(news_feed.feed.keys())

# # Titre du flux
# print("Feed Title:", news_feed.feed.title) 

# # Sous-titre du flux
# print("Feed Subtitle:", news_feed.feed.subtitle)

# # Lien du flux
# print("Feed Link:", news_feed.feed.link, "\n")

# # Propriétés de chaque item du flux
# print(news_feed.entries[0].keys())

# pprint

for entry in news_feed.entries:
    summary = entry.summary
    date = entry.published
    pprint(entry)
    exit()
    print(f"{entry.title} --> {entry.link}")
    print(f"{entry.id}")
    
# # Récupération du deernier feed (dernier bulletin CERT-FR)
# for i in range(0, len(news_feed.entries)):
#     if i == (len(news_feed.entries)-1):
#         print("Alert: {} \nLink: {}".format(news_feed.entries[0]['title'], news_feed.entries[0]['id']))