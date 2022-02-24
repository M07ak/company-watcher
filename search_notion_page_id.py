import argparse, pprint

from notion import search_page_id

parser = argparse.ArgumentParser()
parser.add_argument("--search", help="The text to search in Notion")
args = parser.parse_args()

for result in search_page_id(parser.parse_args().search)["results"]:
    print(f"Found page with id {result['id']}")