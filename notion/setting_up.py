import requests, os
from requests.structures import CaseInsensitiveDict
from pprint import pprint

import utils

def create_source_database(source_database_config):
    return source_database_config

def create_google_news_dashboard(google_news_dashboard_config):
    return google_news_dashboard_config

def create_notion_pages(notion_config):
    for database in notion_config:
        if notion_config[database]["activated"] and "id" not in notion_config[database]:
            if database == "source_database":
                notion_config[database] = create_source_database(notion_config[database])
            elif database == "google_news_dashboard":
                notion_config[database] = create_source_database(notion_config[database])
            elif database == "rss_feed_config_dashboard":
                notion_config[database] = create_source_database(notion_config[database])
            elif database == "news_database":
                notion_config[database] = create_source_database(notion_config[database])
                 


    return notion_config

def setup():
    notion_config = utils.config()
    main_page_content = utils.get_page_content(utils.NOTION_PAGE)
    
    for item in main_page_content:
        if item["type"] == "child_page":
            for database in notion_config:
                if notion_config[database]["activated"] and item["child_page"]["title"] == notion_config[database]["name"]:
                    notion_config[database]["created"] = True
                    notion_config[database]["id"] = item["id"]

    notion_config = create_notion_pages(notion_config)



if __name__ == "__main__":
    setup()
