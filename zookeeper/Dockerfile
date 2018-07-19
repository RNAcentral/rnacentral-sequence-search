FROM nimmis/java-centos:oracle-9-jdk

RUN yum install -y \
    tar \
    unzip \
    wget

# install jdk
#RUN wget http://download.oracle.com/otn-pub/java/jdk/10.0.2+13/19aef61b38124481863b1413dce1855f/jdk-10.0.2_linux-x64_bin.tar.gz
#RUN tar -zxvf jdk-10.0.2_linux-x64_bin.tar.gz
#RUN mv jdk-10.0.2_linux-x64_bin /usr/local/bin

# export Java environment variables
#RUN cat "export JAVA_HOME = /usr/jdk/jdk-1.8.0_60" >> /etc/bashrc
#RUN cat "export PATH=$PATH:$JAVA_HOME/bin" >> /etc/bashrc

# update-alternatives
#RUN update-alternatives --install /usr/bin/java java /usr/local/bin/jdk-10.0.2_linux-x64_bin/bin/java 100

# install zookeeper
RUN curl -OL https://archive.apache.org/dist/zookeeper/zookeeper-3.4.13/zookeeper-3.4.13.tar.gz && \
    tar -zxvf zookeeper-3.4.13.tar.gz && \
    mv zookeeper-3.4.13 /usr/local/bin && \
    cd /usr/local/bin/zookeeper-3.4.13 && \
    mkdir data

ADD zoo.cfg /usr/local/bin/zookeeper-3.4.13/conf/zoo.cfg

CMD /usr/local/bin/zookeeper-3.4.13/bin/zkServer.sh start && /usr/local/bin/zookeeper-3.4.13/bin/zkCli.sh
