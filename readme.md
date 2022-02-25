
# Competitor Alerter
A free competitor RSS and Alert based on Notion and Google alerts
Generate a Feeder RSS config file, sorted by categories to watch your competitors news

NOTION-DATABASE <-> Google Alerts <-> RSS App

A Notion database is used as  a source of companies and keywords names to watch for
Names and keywords are automatically synced with Google alerts RSS generator
Google Alerts RSS urls are collected and merge in a ready to use Feeder config file

## Screenshots
<!-- ![Notion source DB](https://i.imgur.com/D3FCGhU.png "Notion source DB") -->
<p align="center">
  <img src="https://i.imgur.com/D3FCGhU.png" alt="Notion source DB" height="100"/>
    <img src="https://i.imgur.com/obgBluo.png" alt="Google News Dashboard" height="100"/>
    <img src="https://i.imgur.com/eBUnsEF.png" alt="RSS Generator Dashboard" height="100"/>
    <img src="https://i.imgur.com/FTLBStR.png" alt="Feeder Screen 1" height="100"/>
    <img src="https://i.imgur.com/BitlBex.png" alt="Feeder Screen 2" height="100"/>
</p>


## Quick start
Init a seed session based on *Google Alerts* readme 
```
$ docker pull  m07ak/company-watcher:latest
$ docker run --env-file ./.env -v [YOUR_LOCAL_PATH_TO_SEED_CONFIG]:[GOOGLE_ALERT_CONFIG] m07ak/company-watcher:latest
```

## Installation
```
$ git clone --recurse-submodules https://github.com/M07ak/company-watcher.git
```
### On ubuntu
#### Project
```
$ cd company-watcher
$ apt-get -y install chromium-browser python3-selenium
$ pip install -r requirements.txt
```
#### Google Alerts
- In google-alerts submodule
```
$ python setup.py install
```
- Follow Google Alerts readme to Seed your GoogleAlerts configuration from a browser
    - Visit https://github.com/M07ak/google-alerts


### On VsCode with devcontainer extension
- Commands: 
    - Remote-Containers: Rebuild Container
    or
    - Remote-Containers: Reopen in Container

### With docker
* First config .env variable following instructions
```
$ docker pull  m07ak/company-watcher:latest
$ docker run --env-file ./.env -v [YOUR_LOCAL_PATH_TO_SEED_CONFIG]:[GOOGLE_ALERT_CONFIG] m07ak/company-watcher:latest
```

## Configuration
### Environment variables
Copy .env.template into .env and/or .devcontainer/devcontainer.env (if you plan to use Vs Code Devcontainers)
Replace placeholder with your values

<br/>

&nbsp;&nbsp;&nbsp;**NOTION_TOKEN**
* A Notion API Token with permissions on the following Notion pages. See [Notion documentation](https://www.notion.so/help/create-integrations-with-the-notion-api)

&nbsp;&nbsp;&nbsp;**NOTION_SOURCE_DATABASE_PAGE_ID**
* A Notion database ID based on the following example: [Example](https://sustaining-sweater-edb.notion.site/955080b4b95145018382a126aa07170a)

&nbsp;&nbsp;&nbsp;**NOTION_OUTPUT_GOOGLE_NEWS_DASHBOARD_PAGE_ID**
* A Notion **void** page id. This page will be used to generate a Dashboard to quickly browse Google News
* **This page will be overwritten each time the program will be run**
* Example of dashboard generated with the previously defined source example [Dashboard](https://sustaining-sweater-edb.notion.site/Google-News-Dashboard-example-bb8e080bcdaf420499662fbc6a2d4c77)
* To find a page id, you can use the simple cli in this projet, with your **NOTION_TOKEN** in env:
    ```
    python search_notion_page_id.py  --search "The page name"
    ```

&nbsp;&nbsp;&nbsp;**NOTION_OUTPUT_RSS_PAGE_ID**
* A Notion **void** page id. This page will be used to generate a Dashboard to export Feeder config or get raw RSS urls
* **This page will be overwritten each time the program will be run**
* Example of dashboard generated with the previously defined source example [Dashboard](https://sustaining-sweater-edb.notion.site/Rss-Feed-Dashboard-example-d33dc4d340e64f48a3465db1ca6ba8c4)
* To find a page id, you can use the simple cli in this projet, with your **NOTION_TOKEN** in env:
    ```
    python search_notion_page_id.py  --search "The page name"
    ```

&nbsp;&nbsp;&nbsp;**GITHUB_TOKEN**
* A Github personal access token with permission to use Gist [Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

&nbsp;&nbsp;&nbsp;**FEEDER_GIST_ID**
* A Github Gist unique id to save feeder config file output


&nbsp;&nbsp;&nbsp;**GOOGLE_EMAIL**
* A Google acccount email
* **Even though I've never had a problems, I recommend to use a dedicated Google account, to be sure that in case of problem, your real Google account won't be banned**

&nbsp;&nbsp;&nbsp;**GOOGLE_PASSWORD**
* A Google acccount password
* **Even though I've never had a problems, I recommend to use a dedicated Google account, to be sure that in case of problem, your real Google account won't be banned**

&nbsp;&nbsp;&nbsp;**GOOGLE_ALERT_CONFIG**
* A local path to save your Google session

## Usage
### Generate content
* Run program to populate Notion pages
```
$ python3 run.py
```
### Rss feeds
- Export file written in Gist to opml file and import it in Feeder app [Play Store](https://play.google.com/store/apps/details?id=com.nononsenseapps.feeder.play&hl=fr&gl=US)  [F-droid](https://f-droid.org/en/packages/com.nononsenseapps.feeder/)