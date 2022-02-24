import requests
import os
import pprint
import urllib.parse
from requests.structures import CaseInsensitiveDict
from collections import defaultdict

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

RESULT_PAGE_ID = '2e460096-38d6-4db9-86ed-df87ac427d89'
RSS_PAGE_ID = '6d486d44-db90-426c-9936-f4f294fe0195'


# Prepare login info
global headers
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["Authorization"] = f"Bearer {NOTION_TOKEN}"
headers["Notion-Version"] = "2021-08-16"

titles_colors = ["blue", "pink", "orange", "green", "purple", "yellow", "red", "brown", "blue", "pink", "orange", "green", "purple", "yellow", "red", "brown"]


def get_companies_names_to_track_from_notion_database(page_id):
    url = f"https://api.notion.com/v1/databases/{page_id}/query"

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
    
    return companies_names_by_categories, top_companies_names_by_categories


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


