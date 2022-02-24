'''
HTTP Reuests has following parameters: 
1)Request URL 
2)Header Fields
3)Parameter 
4)Request body
'''
#!/usr/bin/env python

import requests
import json
import os, pprint

GITHUB_API="https://api.github.com"
API_TOKEN=os.getenv("GITHUB_TOKEN")

def update_gist_file(gist_id, filename, code, description):
    """Update a Github Gist file with code content and get URL

    Args:
        gist_id (string): A Github gist id
        filename (string): The gist name
        code (string): The gist content
        description (string): The gist description

    Returns:
        string: The gist url
    """
    url=GITHUB_API+"/gists/" + gist_id
    headers={'Authorization':'token %s'%API_TOKEN}
    params={'scope':'gist'}
    payload={"description":description,"public":True,"files":{filename: {"content": code}}}
    reply = requests.patch(url,headers=headers,params=params,data=json.dumps(payload))

    return reply.json()["html_url"]