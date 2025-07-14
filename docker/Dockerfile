FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code
RUN mkdir -p /sock
RUN mkdir -p /logs
WORKDIR /code

COPY apt_requirements.txt /code/
RUN apt-get -y update
RUN cat apt_requirements.txt | xargs apt -y --no-install-recommends install \
	&& rm -rf /var/lib/apt/lists/* \
	&& apt autoremove \
	&& apt autoclean

COPY requirements.txt /code/
RUN pip install --no-cache-dir setuptools==57.5.0
RUN pip install --no-cache-dir -r requirements.txt
RUN rm /code/requirements.txt /code/apt_requirements.txt

ENTRYPOINT /code/entrypoint.sh
