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
    python-pip

COPY producer .

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD python manage.py migrate && python manage.py runserver --nothreading