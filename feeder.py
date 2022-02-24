from collections import defaultdict

template = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.1">
  <head>
    <title>
      Veille
    </title>
  </head>
  <body>
#BODY#
  </body>
</opml>"""

class RssFeed:
    def __init__(self, name, category, rss_link):
        self.name = name
        self.category = category
        self.rss_link = rss_link

def create_feeder_config_file_from_tracking(feeds):
    feeds_by_category = defaultdict(list)
    for feed in feeds:
        feeds_by_category[feed.category].append(feed)
    
    outlines = ""

    for category in feeds_by_category:
        outlines += f'    <outline title="{category}" text="{category}">\n'
        for feed in feeds_by_category[category]:
            outlines += f'      <outline title="{feed.name}" type="rss" xmlUrl="{feed.rss_link}"/>\n'
        outlines += '    </outline>\n'
    
    output = template.replace("#BODY#", outlines)

    with open("/tmp/feeder.opml", "w+") as feeder_output:
        feeder_output.write(output)
    
    return "/tmp/feeder.opml"


if __name__ == "__main__":
    feeds = [RssFeed("Test", "Startup", "https://google.com")]
    create_feeder_config_file_from_tracking(feeds)