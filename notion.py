from pprint import pprint
import requests
import os
import urllib.parse
from requests.structures import CaseInsensitiveDict
from collections import defaultdict

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_COLORS = ["blue", "pink", "orange", "green", "purple", "yellow", "red", "brown"]

# Prepare login info
global headers
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["Authorization"] = f"Bearer {NOTION_TOKEN}"
headers["Notion-Version"] = "2021-08-16"


titles_colors = NOTION_COLORS + NOTION_COLORS + NOTION_COLORS



def set_company_rss_url(page_id, url):
    properties = {
        "rss": {"url": url}
    }
    print(f"Set RSS url of {page_id} to {url}")
    notion_update_properties(page_id, properties)

def notion_update_properties(page_id, properties):
    """Update a Notion page properties

    Args:
        page_id (string): A notion page id
        properties (dict): A dict of properties with their values to update
    """
    data = {
        "properties": properties
    }

    global headers

    url = f"https://api.notion.com/v1/pages/{page_id}"

    requests.patch(url, headers=headers, json=data)


def search_page_id(term):
    # Search for a page
    url = f"https://api.notion.com/v1/search"

    data = {
        "query": term,
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time"
        }
    }

    resp = requests.post(url, headers=headers, json=data)

    return resp.json()

def get_page_content(page_id):
    global headers
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"

    result = requests.get(url, headers=headers)

    return result.json()["results"]
    

def get_rss_news_from_notion_db(page_id, min_publication_date):
    """Get a list of rss news from Notion db

    Args:
        page_id (string): A Notion page id

    Returns:
        list: A list of rss news
    """

    results = []

    url = f"https://api.notion.com/v1/databases/{page_id}/query"

    data = {
        "page_size": 25,
        "filter": {
            "and": [
                {
                    "property": "Date de publication",
                    "date": {
                        "on_or_after": min_publication_date.isoformat()
                    }
                }
            ]
        },
        "sorts": [
            {
                "property": "Date de publication",
                "direction": "descending"
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=data)
    json_resp = resp.json()
    results += resp.json()["results"]

    while json_resp["next_cursor"]:
        # Query all data following given cursor
        data["start_cursor"] = json_resp["next_cursor"]
        resp = requests.post(url, headers=headers, json=data)
        json_resp = resp.json()
        results += resp.json()["results"]

    return results

def get_companies_from_notion_db(page_id):
    """Get a list of companies from Notion DB

    Args:
        page_id (string): A Notion page id

    Returns:
        list: A list of Notion "Company" items
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
    
    return resp.json()["results"]


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

    print(result.json())


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

def notion_post_rss_item(data):
    global headers
    # Current output page blocks
    url = f"https://api.notion.com/v1/pages"
    
    result = requests.post(url, headers=headers, json=data)
    # print(result.json())
    print("Notion item created")

def notion_prepare_rss_item(database_id, company_id, tag, title, summary, publication_date, url, source="inconnue"):
    # publication_date = publication_date.strftime("%Y-%m-%dT%H:%M:%S.%f%Z+01:00")
    publication_date = publication_date.isoformat()
    data = {
        "parent": { "database_id": database_id },
        'icon': {'emoji': '📰', 'type': 'emoji'},
        'properties': {
            'Company': {
                'relation': [{'id': company_id}],
                'type': 'relation'
            },
            "Source": {
                "select": {
                    "name": source
                }
            },
            'Date de publication': {
                'date': {
                    'end': None,
                    'start': publication_date,
                    'time_zone': None
                },
                'type': 'date'
            },
            'Résumé': {
                'rich_text': [{
                    'annotations': {
                        'bold': False,
                        'code': False,
                        'color': 'default',
                        'italic': False,
                        'strikethrough': False,
                        'underline': False
                    },
                    'href': None,
                    'plain_text': summary,
                    'text': {
                        'content': summary,
                        'link': None
                    },
                    'type': 'text'
                }],
                'type': 'rich_text'
            },
            'Titre': {
                'title': [{
                    'annotations': {
                        'bold': False,
                        'code': False,
                        'color': 'default',
                        'italic': False,
                        'strikethrough': False,
                        'underline': False
                    },
                    'href': None,
                    'plain_text': title,
                    'text': {
                        'content': title,
                        'link': None
                    },
                    'type': 'text'
                }],
                'type': 'title'
            },
            'Tag': {
                'rich_text': [{
                    'annotations': {
                        'bold': False,
                        'code': False,
                        'color': 'default',
                        'italic': False,
                        'strikethrough': False,
                        'underline': False
                    },
                    'href': None,
                    'plain_text': tag,
                    'text': {
                        'content': tag,
                        'link': None
                    },
                    'type': 'text'
                }],
                'type': 'rich_text'
            },
            'Url': {
                'type': 'url',
                'url': url
            }
        }
    }
    return data


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
        # print(f"Delete {block['type']}")


