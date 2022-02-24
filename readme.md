# Installation on a fresh Ubuntu
## Common
```
$ git clone --recurse-submodules https://github.com/M07ak/company-watcher.git
$ cd company-watcher
$ apt-get -y install chromium-browser python3-selenium
$ pip install -r requirements.txt
```
## Google Alerts
- In google-alerts submodule
```
$ python setup.py install
```
- Follow Google Alerts readme to Seed your GoogleAlerts configuration from a browser
    - Visit https://github.com/M07ak/google-alerts


# Installation with VsCode devcontainer extension
- Commands: 
    - Remote-Containers: Rebuild Container
    or
    - Remote-Containers: Reopen in Container

# Run
```
$ python3 veille.py
```