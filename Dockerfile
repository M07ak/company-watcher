FROM python:3.10


RUN apt-key adv --fetch-keys "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xea6e302dc78cc4b087cfc3570ebea9b02842f111" \
&& echo 'deb http://ppa.launchpad.net/chromium-team/beta/ubuntu bionic main ' >> /etc/apt/sources.list.d/chromium-team-beta.list \
&& apt update \
&& export DEBIAN_FRONTEND=noninteractive \
&& export DEBCONF_NONINTERACTIVE_SEEN=true \
&& apt-get -y install chromium-browser \
&& apt-get -y install python3-selenium \
&& mkdir /app

COPY requirements.txt /tmp/pip-tmp/
COPY google-alerts/ /app/google-alerts/

RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp && cd /app/google-alerts/ && python setup.py install

WORKDIR /app

copy . /app/

CMD python run.py
