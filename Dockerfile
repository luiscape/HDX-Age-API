##################################################
# Ageing service: calculates how old datasets are
# on HDX. Receives link from a Redis container.
##################################################

FROM ubuntu:latest

MAINTAINER Luis Capelo <capelo@un.org>

USER root

#
# Installing Python 2.7.10
#
RUN \
  apt-get update \
  && apt-get -y upgrade \
  && apt-get install -y software-properties-common build-essential libffi-dev libssl-dev \
  && add-apt-repository ppa:fkrull/deadsnakes \
  && apt-get -y install wget git \
  && apt-get -y install python2.7 python2.7-dev python-dev python-distribute python-pip python-virtualenv

#
# Upgrading pip.
#
RUN \
  wget https://bootstrap.pypa.io/get-pip.py \
  && python get-pip.py \
  && pip --version \
  && python --version

#
# Clone app and install dependencies.
#
RUN \
  git clone http://github.com/luiscape/hdx-monitor-ageing-service \
  && cd hdx-monitor-ageing-service \
  && make setup

WORKDIR "/hdx-monitor-ageing-service"

EXPOSE 3000

CMD ["make", "run"]
