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

RUN curl -OL http://eddylab.org/software/hmmer/hmmer-3.2.1.tar.gz && \
    tar -zxvf hmmer-3.2.1.tar.gz && \
    cd hmmer-3.2.1 && \
    ./configure --prefix /usr/local && \
    make && \
    make install && \
    cd easel; make install

ADD sequence_search/requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 8000

ENV LC_ALL=en_US.utf-8 LANG=en_US.utf-8

ENTRYPOINT cd /rnacentral && adev runserver sequence_search/consumer/__main__.py
