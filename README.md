# Non-coding RNA Sequence Search Repository DevOps code

This repository contains DevOps code for managing a non-coding RNA Sequence Search microservice infrastructure.

Basically, it provides a set of Jenkinsfiles for managing Sequence Search infrastructure as a
Kubernetes cluster on top of EBI OpenStack. Internally those Jenkinsfiles rely upon a set of bash scripts,
Ansible playbooks and OpenStack console client commands.

Unfortunately, Red Hat OpenStack doesn't support the Magnum API that allows for provisioning a Kubernetes
clusters from the console. Thus, we had to resort to Kubespray scipts.


## Installation

The project is supposed to be run in 4 environments:
 - local:
     when developing new features, both producer and consumer are
     supposed to be run from local machine and postgres database server
     is also meant to be run on localhost:5432
 - test:
    this environment is used for running unit-tests on local machine only,
    it is not using any database or network communications
 - docker-compose
    when running manual quality assurance tests on a single machine, this
    environment is deployed with docker-compose up and create containers
    with producer, consumer and postgres
 - production
    this is the real production environment, where the code is deployed
    to openstack cloud


### Installation in local environment

1. `$ git clone https://github.com/RNAcentral/rnacentral-sequence-search.git`
2. `$ cd rnacentral-sequence-search`
3. `$ virtualenv ENV --python=python3`
4. `$ source ENV/bin/activate`
5. `$ pip3 install -r requirements.txt`
6. `$ pushd sequence_search/consumer`
7. `$ curl -OL http://eddylab.org/software/hmmer/hmmer-3.2.1.tar.gz && \
    tar -zxvf hmmer-3.2.1.tar.gz && \
    cd hmmer-3.2.1 && \
    ./configure --prefix /usr/local && \
    make && \
    make install && \
    cd easel; make install`
8. `$ rsync <> databases/` - copy `.fasta` files with databases we want to search against
9. `$ popd`
10. `$ cd sequence_search/producer/static`
11. `$ npm install --save-dev && npm run build`
12. `$ popd`
13. `$ brew install postgres` - install a local postgres database and start it
14. create role `burkov` with password `example` and database `producer` in your local postgres


### Installation in docker-compose

TODO

### Installation in production

Suppose that you want to install this set of Jenkins pipelines to an entirely new machine.

Here are the steps required to do this:

- Install and configure Jenkins on that machine
- In Jenkins interface create a one-branch pipeline for each `*.jenkinsfile` in `/jenkins` folder
- In Jenkins upload secret file `openstack.rc` copied from RedHat Horizon dashboard
 (Project -> Compute -> Access & Security -> API Access)
- Install python-based dependencies via `pip install -r requirements.txt` (possibly, using a virtualenv)


#### How to create .iso image from databases folder on MacOS

 The command is like this:

 `hdiutil makehybrid -o ~/Desktop/image.iso ~/path/to/folder/to/be/converted -iso -joliet`

 Links:

 - https://matt.berther.io/2008/12/14/creating-iso-images-from-a-folder-in-osx/

## "Sources of inspiration"

Code in this repository is based on the following projects by other folks (kudos to them):

- https://github.com/pcm32/kubespray-ebi-portal/tree/v2.3.0-ubuntu-xenial - my Kubespray customization scripts are based on this
- https://github.com/kubernetes-incubator/kubespray/blob/master/upgrade-cluster.yml - Kubespray ansible commands
- https://cloudbase.it/easily-deploy-a-kubernetes-cluster-on-openstack/ - OpenStack console client commands
- https://docs.oracle.com/cd/E36784_01/html/E54155/clicreatevm.html - example OpenStack provisioning commands
- https://github.com/kubernetes-incubator/kubespray - Kubespray main repo
- https://gist.github.com/yonglai/d4617d6914d5f4eb22e4e5a15c0e9a03 - Ansible gist for installing Docker
- https://tasdikrahman.me/2017/03/19/Organising-tasks-in-roles-using-Ansible/ - plays vs roles vs tasks
- https://github.com/ANXS/postgresql - Ansible postgres role
- https://www.ajg.id.au/2018/05/23/ansible-ssh-jump-hosts-and-multiple-private-keys/ - working with jumphosts
- https://platform9.com/blog/how-to-use-terraform-with-openstack/ - sample Terraform/OpenStack configuration
- https://github.com/diodonfrost/terraform-openstack-examples/tree/master/01-sample-instance - more Terraform examples
- https://heapanalytics.com/blog/engineering/terraform-gotchas - explanation of Terraform configuration
