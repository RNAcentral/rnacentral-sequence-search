FROM centos:7

RUN yum -y --enablerepo=extras install epel-release
RUN yum -y update
RUN yum install -y \
    curl \
    gcc \
    git \
    libaio \
    "nc.x86_64" \
    openssl \
    openssl-devel \
    tar \
    unzip \
    wget \
    zlib-devel \
    gcc-c++ \
    make \
    python36 \
    python36-devel \
    python36-setuptools

RUN easy_install-3.6 pip

ADD sequence_search/requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 8002

# to get around click python 3 warnings
ENV LC_ALL=en_US.utf-8 LANG=en_US.utf-8

ENTRYPOINT cd /rnacentral && python36 -m sequence_search.db && adev runserver --port 8002 sequence_search/producer/__main__.py
