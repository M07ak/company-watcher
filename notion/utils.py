import os, json, requests
from requests.structures import CaseInsensitiveDict

NOTION_COLORS = ["blue", "pink", "orange", "green", "purple", "yellow", "red", "brown"]

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE = os.getenv("NOTION_PAGE")


def headers():
    headers_dict = CaseInsensitiveDict()
    headers_dict["Content-Type"] = "application/json"
    headers_dict["Authorization"] = f"Bearer {NOTION_TOKEN}"
    headers_dict["Notion-Version"] = "2021-08-16"
    return headers_dict

def config():
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/../config.json", 'r') as f:
        data = json.load(f)
    return data["notion"]

def get_page_content(page_id):
    """Get a notion page content

    Args:
        page_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"

    result = requests.get(url, headers=headers())

    return result.json()["results"]