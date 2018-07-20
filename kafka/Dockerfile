FROM nimmis/java-centos:oracle-9-jdk

RUN yum install -y \
    tar \
    unzip \
    wget \
    less

# download kafka
RUN curl -OL http://apache.mirror.anlx.net/kafka/1.1.0/kafka_2.11-1.1.0.tgz && \
    tar -zxvf kafka_2.11-1.1.0.tgz && \
    mv kafka_2.11-1.1.0 /usr/local/bin

COPY wrapper.sh .
RUN chmod +x wrapper.sh
CMD ./wrapper.sh