FROM python:3.4
RUN apt-get update
RUN apt-get install -y vim
RUN pip install pipenv
RUN apt-get install -y openssh-server
RUN useradd -ms /bin/bash felipedev
USER felipedev
WORKDIR /home/felipedev/
RUN mkdir code


