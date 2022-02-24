import requests
import os
import pprint
import urllib.parse
from requests.structures import CaseInsensitiveDict
from collections import defaultdict

from google import Term, track_terms
from feeder import RssFeed, create_feeder_config_file_from_tracking
from github import update_gist_file

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SOURCE_PAGE_ID = '05b1b958-01f1-4045-ab81-cd2e2eba55e2'
RESULT_PAGE_ID = '2e460096-38d6-4db9-86ed-df87ac427d89'
RSS_PAGE_ID = '6d486d44-db90-426c-9936-f4f294fe0195'
GOOGLE_NEWS_MAX_SIZE = 12

FEEDER_GIST_ID=os.getenv("FEEDER_GIST_ID")

global headers
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["Authorization"] = f"Bearer {NOTION_TOKEN}"
headers["Notion-Version"] = "2021-08-16"

titles_colors = ["blue", "pink", "orange", "green", "purple", "yellow", "red", "brown", "blue", "pink", "orange", "green", "purple", "yellow", "red", "brown"]

url = f"https://api.notion.com/v1/blocks/{SOURCE_PAGE_ID}/children?page_size=100"


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


def notion_add_blocks(parent_block_id, blocks):
    global headers
    # Current output page blocks
    url = f"https://api.notion.com/v1/blocks/{parent_block_id}/children"

    data = {
        "children": blocks
    }

    result = requests.patch(url, headers=headers, json=data)


def notion_create_title_object(title, level=1, random_color=False):
    if random_color:
        color = titles_colors.pop(0)
    else:
        color = "default"

    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {
            "text": [
                {
                    "type": "text",
                    'annotations': {
                        'bold': False,
                        'code': False,
                        'color': color,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False
                    },
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    }

def notion_create_code_object(code):
    return {
        "object": "block",
        "type": "code",
        "code": {'caption': [],
           'language': 'xml',
           'text': [{'annotations': {'bold': False,
                                     'code': False,
                                     'color': 'default',
                                     'italic': False,
                                     'strikethrough': False,
                                     'underline': False},
                     'href': None,
                     'plain_text': "ee",
                     'text': {'content': code,
                              'link': None},
                     'type': 'text'}]}
    }


def notion_create_links_paragraph(links):
    blank_space = {
        'annotations': {
            'bold': False,
            'code': False,
            'color': 'default',
            'italic': False,
            'strikethrough': False,
            'underline': False
        },
        'href': None,
        'plain_text': '    ',
        'text': {'content': ' ', 'link': None},
        'type': 'text'
    }

    links_with_blank_space = []
    for link_object in links:
        links_with_blank_space.append(link_object)
        links_with_blank_space.append(blank_space)
        links_with_blank_space.append(blank_space)
        links_with_blank_space.append(blank_space)

    return {
        'paragraph': {'text': links_with_blank_space},
        'type': 'paragraph'
    }


def notion_create_text_paragraph(text):
    return {
        'paragraph': {'text': [
            {
        'annotations': {
            'bold': False,
            'code': False,
            'color': 'default',
            'italic': False,
            'strikethrough': False,
            'underline': False
        },
        'href': None,
        'plain_text': text,
        'text': {'content': text, 'link': None},
        'type': 'text'
    }
        ]},
        'type': 'paragraph'
    }

def notion_create_link_object(url, text):
    return {'annotations': {'bold': False,
                            'code': False,
                            'color': 'default',
                            'italic': False,
                            'strikethrough': False,
                            'underline': False},
            'href': url,
            'plain_text': text,
            'text': {'content': text,
                     'link': {'url': url}},
            'type': 'text'}


def populate_page_with_columns(page_id, columns):
    # Create columns
    parsed_columns = []
    for column in columns:
        parsed_columns.append({
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": column
                            }
                        })
    
    data = {
        "children": [
            {
                "object": "block",
                "type": "column_list",
                "column_list": {
                    "children": parsed_columns
                }
            }
        ]
    }

    global headers
    # Current output page blocks
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"

    result = requests.patch(url, headers=headers, json=data)


def notion_clear_page(page_id):
    global headers

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"

    resp = requests.get(url, headers=headers)

    # pprint.pprint(resp.json()["results"])
    # exit()

    for block in resp.json()["results"]:
        # pprint.pprint(block)
        url = f"https://api.notion.com/v1/blocks/{block['id']}"

        resp = requests.delete(url, headers=headers)
        print(f"Delete {block['type']}")
    # exit()
    # pprint.pprint(output_block)

# Search for a page
# url = f"https://api.notion.com/v1/search"

# data = {
#     "query": "Flux RSS",
#     "sort": {
#         "direction": "ascending",
#         "timestamp": "last_edited_time"
#     }
# }

# resp = requests.post(url, headers=headers, json=data)

# pprint.pprint(resp.json())

# exit()

# Get companies in veille DB



# create_and_get_page_columns(RESULT_PAGE_ID, 3)
# exit()
url = f"https://api.notion.com/v1/databases/{SOURCE_PAGE_ID}/query"

data = {
    "filter": {
        "or": [
        ]
    },
    "sorts": [
        {
            "property": "Niveau d'intéret",
            "direction": "ascending"
        }
    ]
}

resp = requests.post(url, headers=headers, json=data)
companies_names_by_categories = defaultdict(list)
top_companies_names_by_categories = defaultdict(list)

for company in resp.json()["results"]:
    if company["properties"]["Catégorie"]["select"]:
        category = company["properties"]["Catégorie"]["select"]["name"]
    else:
        category = "Sans catégorie"

    if not company["properties"]["Google News"]["checkbox"]:
        continue

    if company["properties"]["Niveau d'intéret"]["number"]:
        score = company["properties"]["Niveau d'intéret"]["number"]
    else:
        score = 0

    try:
        name = company["properties"]["Name"]["title"][0]["plain_text"]
    except:
        continue

    # companies_names.append(name)
    if score > 9:
        top_companies_names_by_categories[category].append(name)

    companies_names_by_categories[category].append(name)


new_notion_blocks = []
columns = []

# Google alert tracking part

notion_clear_page(RSS_PAGE_ID)

list_of_rss_notion_links = []

tracking_by_category = defaultdict(list)
terms_to_track = []

for category in companies_names_by_categories:
    for name in companies_names_by_categories[category]:
        new_term = Term(name=name, category=category)
        tracking_by_category[category].append(new_term)
        terms_to_track.append(new_term)


feeds_to_add = []

terms_to_track = track_terms(terms_to_track)
for term in terms_to_track:
    feeds_to_add.append(RssFeed(name=term.name, category=term.category, rss_link=term.rss_url))
    list_of_rss_notion_links.append(notion_create_text_paragraph(term.rss_url))

local_file_path = create_feeder_config_file_from_tracking(feeds_to_add)

rss_to_add_notion = []

rss_to_add_notion.append(notion_create_title_object("Config Feeder", 1, random_color=False))
code = ""
# with open("/tmp/feeder.opml", "r") as feeder_config_file:
with open(local_file_path, "r") as feeder_config_file:
    for line in feeder_config_file:
        code+=line
        # print(line)

gist_url = update_gist_file(gist_id=FEEDER_GIST_ID, filename="config.opml", code=code, description="A Feeder config file")

link_object = notion_create_link_object(url=gist_url, text="feeder.opml")
rss_to_add_notion.append(notion_create_links_paragraph([link_object]))

rss_to_add_notion.append(notion_create_title_object("Liste des flux", 1, random_color=False))
rss_to_add_notion += list_of_rss_notion_links

notion_add_blocks(RSS_PAGE_ID, rss_to_add_notion)


# Notion output part

notion_clear_page(RESULT_PAGE_ID)

for category in companies_names_by_categories:
    column = []
    column.append(notion_create_title_object(
        category, 1, random_color=True))

    if top_companies_names_by_categories[category]:
        column.append(notion_create_title_object("TOP", 2))
        column.append(notion_create_title_object("News de la semaine", 3))
        i = 1
        links_list = []
        for url in geneate_google_news_search_urls(top_companies_names_by_categories[category], time_range="7d"):
            links_list.append(
                notion_create_link_object(url, f"Partie {i}"))
            i += 1
        column.append(notion_create_links_paragraph(links_list))
        column.append(notion_create_title_object("News du mois", 3))
        i = 1
        links_list = []
        for url in geneate_google_news_search_urls(top_companies_names_by_categories[category], time_range="31d"):
            links_list.append(
                notion_create_link_object(url, f"Partie {i}"))
            i += 1
        column.append(notion_create_links_paragraph(links_list))

        column.append(notion_create_title_object("ALL", 2))
    
    column.append(notion_create_title_object("News de la semaine", 3))
    i = 1
    links_list = []
    for url in geneate_google_news_search_urls(companies_names_by_categories[category], time_range="7d"):
        links_list.append(notion_create_link_object(url, f"Partie {i}"))
        i += 1
    column.append(notion_create_links_paragraph(links_list))
    column.append(notion_create_title_object("News du mois", 3))
    i = 1
    links_list = []
    for url in geneate_google_news_search_urls(companies_names_by_categories[category], time_range="31d"):
        links_list.append(notion_create_link_object(url, f"Partie {i}"))
        i += 1
    column.append(notion_create_links_paragraph(links_list))
    columns.append(column)


populate_page_with_columns(RESULT_PAGE_ID, columns)
# notion_add_blocks(RESULT_PAGE_ID, new_notion_blocks)

# google_urls = geneate_google_news_search_urls(companies_names, time_range="7d")


# Add block

# notion_clear_page(RESULT_PAGE_ID)
# notion_add_title(RESULT_PAGE_ID, "Titre trop bien", level=1)
# notion_add_link(RESULT_PAGE_ID, "https://google.com", "Google")

# pprint.pprint(companies_names_by_categories)
# pprint.pprint(top_companies_names_by_categories)
# print(resp.json())
