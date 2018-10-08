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

ADD requirements.txt .

RUN pip3 install -r requirements.txt

CMD python36 -m producer.models && python36 -m producer.main
