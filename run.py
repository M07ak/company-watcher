import requests
import os
import pprint

from collections import defaultdict

from google import Term, track_terms, geneate_google_news_search_urls
from feeder import RssFeed, create_feeder_config_file_from_tracking
from github import update_gist_file
import notion


NOTION_SOURCE_DATABASE_PAGE_ID = os.getenv("NOTION_SOURCE_DATABASE_PAGE_ID")
NOTION_OUTPUT_GOOGLE_NEWS_DASHBOARD_PAGE_ID = os.getenv("NOTION_OUTPUT_GOOGLE_NEWS_DASHBOARD_PAGE_ID")
NOTION_OUTPUT_RSS_PAGE_ID = os.getenv("NOTION_OUTPUT_RSS_PAGE_ID")

FEEDER_GIST_ID=os.getenv("FEEDER_GIST_ID")

"""Notion source"""
# Get companies names from Notion source database
print("List companies from Notion")
companies_names_by_categories, top_companies_names_by_categories = notion.get_companies_names_to_track_from_notion_database(NOTION_SOURCE_DATABASE_PAGE_ID)

for category in companies_names_by_categories:
    print(f"Found {len(companies_names_by_categories[category])} companies with category {category}")

# """Google Alerts"""

# Generate Googles Alerts from companies names

tracking_by_category = defaultdict(list)
terms_to_track = []

# Prepare list of terms to track
for category in companies_names_by_categories:
    for name in companies_names_by_categories[category]:
        new_term = Term(name=name, category=category)
        tracking_by_category[category].append(new_term)
        terms_to_track.append(new_term)

# Create and delete Google Alerts tracking to match terms to track
print("Track companies names on Google alerts")
terms_to_track = track_terms(terms_to_track)


"""Parsing"""
list_of_rss_notion_links = []
feeds_to_add = []

for term in terms_to_track:
    # Prepare list of RssFeed to export
    feeds_to_add.append(RssFeed(name=term.name, category=term.category, rss_link=term.rss_url))


"""Feeder & RSS"""
print("Generate RSS links and config file")

# Export list of RssFeed into Feeder config file
local_file_path = create_feeder_config_file_from_tracking(feeds_to_add)

# Update a gist on Github with newly created Feeder config file
with open(local_file_path, "r") as feeder_config_file:
    local_file_code = "".join(feeder_config_file.readlines())

    gist_url = update_gist_file(gist_id=FEEDER_GIST_ID, filename="config.opml", code=local_file_code, description="A Feeder config file")

# Populate Rss Notion Output page with created file and raw RSS urls

print("Populate RSS Notion dashboard")

notion.notion_clear_page(NOTION_OUTPUT_RSS_PAGE_ID)

notion_blocks_to_add_to_page = []

# Create notion title
notion_blocks_to_add_to_page.append(notion.notion_create_title_object("Feeder config", 1))

# Add link for feeder config file to Notion page
notion_blocks_to_add_to_page.append(notion.notion_create_links_paragraph([notion.notion_create_link_object(url=gist_url, text="feeder.opml")]))

# Add notion title
notion_blocks_to_add_to_page.append(notion.notion_create_title_object("Flux RSS", 1))

rss_links_to_add = []

for term in terms_to_track:
    # Extract list of rss links and add it to Notion
    rss_links_to_add.append(notion.notion_create_text_paragraph(term.rss_url))

# Add links to Notion
notion_blocks_to_add_to_page += rss_links_to_add

notion.notion_add_blocks(NOTION_OUTPUT_RSS_PAGE_ID, notion_blocks_to_add_to_page)



"""Notion Google News watching dashboard"""
print("Populate Google News Notion dashboard")
notion.notion_clear_page(NOTION_OUTPUT_GOOGLE_NEWS_DASHBOARD_PAGE_ID)

columns = []

# Parse Google News simple URL and add them to Notion Dashboard page
for category in companies_names_by_categories:
    # Divide page in columns
    column = []

    # 1 column for each category
    column.append(notion.notion_create_title_object(category, 1, random_color=True))

    # If companies are more relevant than others, separate them from other in TOP part
    # Create links to watch weekly news and montly news
    if top_companies_names_by_categories[category]:
        column.append(notion.notion_create_title_object("TOP", 2))
        column.append(notion.notion_create_title_object("News de la semaine", 3))
        i = 1
        links_list = []
        # Populate page with Google News urls
        for url in geneate_google_news_search_urls(top_companies_names_by_categories[category], time_range="7d"):
            links_list.append(
                notion.notion_create_link_object(url, f"Partie {i}"))
            i += 1
        column.append(notion.notion_create_links_paragraph(links_list))
        column.append(notion.notion_create_title_object("News du mois", 3))
        i = 1
        links_list = []
        for url in geneate_google_news_search_urls(top_companies_names_by_categories[category], time_range="31d"):
            links_list.append(
                notion.notion_create_link_object(url, f"Partie {i}"))
            i += 1
        column.append(notion.notion_create_links_paragraph(links_list))

        column.append(notion.notion_create_title_object("ALL", 2))
    
    # Create links for all tracked companies
    column.append(notion.notion_create_title_object("News de la semaine", 3))
    i = 1
    links_list = []
    for url in geneate_google_news_search_urls(companies_names_by_categories[category], time_range="7d"):
        links_list.append(notion.notion_create_link_object(url, f"Partie {i}"))
        i += 1
    column.append(notion.notion_create_links_paragraph(links_list))
    column.append(notion.notion_create_title_object("News du mois", 3))
    i = 1
    links_list = []
    for url in geneate_google_news_search_urls(companies_names_by_categories[category], time_range="31d"):
        links_list.append(notion.notion_create_link_object(url, f"Partie {i}"))
        i += 1
    column.append(notion.notion_create_links_paragraph(links_list))
    columns.append(column)


# Add columns to dashboard Notion output page
notion.populate_page_with_columns(NOTION_OUTPUT_GOOGLE_NEWS_DASHBOARD_PAGE_ID, columns)