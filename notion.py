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
    """Get a list of companies names, with corresponding categories from Notion source "Veille" database page

    Args:
        page_id (string): A Notion page id

    Returns:
        (dict, dict): Dicts of companies names, by category (top and all) 
    """
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
        # Extract properties from database item withotu failure
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
        
        # Add company as a "top" company if score is high
        if score > 9:
            top_companies_names_by_categories[category].append(name)

        companies_names_by_categories[category].append(name)
    
    return companies_names_by_categories, top_companies_names_by_categories


def notion_add_blocks(parent_block_id, blocks):
    """Add a block to Notion

    Args:
        parent_block_id (string): A Notion block id
        blocks (list): A list of Notion blocks
    """
    global headers

    # Append blocks to Notion page
    url = f"https://api.notion.com/v1/blocks/{parent_block_id}/children"

    data = {
        "children": blocks
    }
    result = requests.patch(url, headers=headers, json=data)


def notion_create_title_object(title, level=1, random_color=False):
    """Create a Notion title object with annotations

    Args:
        title (string): A title text
        level (int, optional): Notion title level. Defaults to 1.
        random_color (bool, optional): Pop a color from Notion available color. Defaults to False.

    Returns:
        NotionTitle: A Notion title object
    """
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

def notion_create_links_paragraph(links):
    """Create a Notion line of links separated by blank spaces

    Args:
        links (list): A list of Notion links objects

    Returns:
        NotionParagraph: A Notion paragraph
    """

    blank_space_number = 3
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
        for i in range(blank_space_number):
            links_with_blank_space.append(blank_space)

    return {
        'paragraph': {'text': links_with_blank_space},
        'type': 'paragraph'
    }


def notion_create_text_paragraph(text):
    """Create a Notion simple paragraph

    Args:
        text (string): A text

    Returns:
        NotionParagraph: A Notion paragraph
    """
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
    """Create a Notion link object

    Args:
        url (string): A link url
        text (string): A link name

    Returns:
        NotionLink: A Notion link object
    """
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
    """Append columns to a Notion page

    Args:
        page_id (string): A Notion page id
        columns (list): A list of Notion Column objects
    """
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
    """Remove all block from a Notion page

    Args:
        page_id (string): A Notion page id
    """
    global headers

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"

    resp = requests.get(url, headers=headers)

    for block in resp.json()["results"]:
        url = f"https://api.notion.com/v1/blocks/{block['id']}"

        resp = requests.delete(url, headers=headers)
        print(f"Delete {block['type']}")


