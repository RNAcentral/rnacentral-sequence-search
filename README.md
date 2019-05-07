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
5. `$ pip3 install -r sequence_search/requirements.txt`
6. `$ pushd sequence_search/consumer`
7. `$ curl -OL http://eddylab.org/software/hmmer/hmmer-3.2.1.tar.gz && \
    tar -zxvf hmmer-3.2.1.tar.gz && \
    cd hmmer-3.2.1 && \
    ./configure --prefix /usr/local && \
    make && \
    make install && \
    cd easel; make install`
8. `$ rsync <database/fasta/files/location/on/local/machine> databases/` - copy `.fasta` files with databases we want to search against into `sequence_search/consumer/databases folder`
9. Update the contents of `sequence_search/consumer/rnacentral_database.py` accordingly (there's a mapping of database human-readable names to file names).
10. `$ popd`
11. `$ pushd sequence_search/producer/static`
12. `$ npm install --save-dev && npm run build`
13. `$ popd`
14. Edit `postgres/local_init.sql` file and replace role `burkov` there with your username on local machine
15. Edit `sequence_search/db/settings.py` and replace role `burkov` with your username on local machine
16. `$ mkdir sequence_search/consumer/queries` - create queries directory in consumer
17. `$ mkdir sequence_search/consumer/results` - create results directory in consumer
18. `$ docker build -t local-postgres -f postgres/local.Dockerfile postgres` - this will create an image with postgres databases.
19. `$ docker run -d -p 5432:5432 -t local-postgres` - this will create and start an instance of postgres on your local machine's 5432 port.
20. `python3 -m sequence_search.db` - creates necessary database tables for producer and consumer to run
21. `python3 -m sequence_search.producer` - starts producer server on port 8002
22. `python3 -m sequence_search.consumer` - starts consumer server on port 8000


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

### Manual deployment in production

Requirements: install Terraform and install dependencies in the virtual environment.

1. Generate `sequence_search_rsa` key:

  `cd terraform && ssh-keygen -t rsa -b 4096`

  See: https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

2. Follow steps in `redeploy.jenkinsfile`.

  - Install SSH keys
  - Run `terraform init && terraform apply` to create the infrastructure
  - Run ansible to create postgres database
  - Run ansible to create producer instance
  - Run ansible to create consumer instances

#### How to upload image with databases to openstack

See: https://matt.berther.io/2008/12/14/creating-iso-images-from-a-folder-in-osx/

1. To create an .iso image from databases folder on your MacOS:

 `cd sequence_search/consumer`

 `hdiutil makehybrid -o databases.iso databases -iso -joliet`

2. To upload image to the cloud first download openstack.rc from Horizon dashboard

3. Source it: `source openstack.rc`, enter your user's password

4. Create a glance image:

 `glance image-create --name sequence_search_databases --disk-format=iso --container-format=bare --file databases.iso`


#### How to dynamically generate ansible inventory from terraform state

1. (a) Install terraform inventory (https://github.com/adammck/terraform-inventory):

`brew install terraform-inventory`

1. (b) Alternatively, download and install platform-specific distribution from here:

https://github.com/adammck/terraform-inventory/releases

2. Create terraform infrastructure:

`pushd terraform; terraform apply; popd`

3. Generate the ansible inventory from terraform state and save it to hosts file:

`terraform-inventory -inventory terraform/terraform.tfstate > ansible/hosts`

4. You can run ansible commands now with:

`pushd ansible; ansible-playbook -i hosts ...`


#### How to work build frontend

Frontend code of the producer is available in `producer/static`.

You build the frontend with `npm run build` command, which goes to
`package.json` file's 'scripts' section and finds and executes 'build'
script. You might want to inspect other scripts from that file.

The build system in this project is Webpack. Its main configuration file
is `producer/static/webpack.config.js`.

All the frontend assets reside either in `producer/static/src` or in
`producer/static/node_modules`. Webpack builds them, putting javascript,
css, icons and fonts files into `producer/static/dist` folder, while
putting references to them into `producer/static/index.html` (not in
`dist`, because it needs to be served by aiohttp server from the root
of `static` folder) which is generated from
`producer/static/src/index.html` template.

For local development, there's also a configuration for
webpack-dev-server. Dev server serves on port 8080 and proxies requests
to the backend to the real server (see the last part of
`webpack.config.js` for the webpack-dev-server configuration).

We're using Webpack 3 here. Webpack 4 was released recently, its
configuration is somewhat different. See its docs here:
https://webpack-v3.jsx.app/ or lookup here:
https://github.com/webpack/webpack.js.org/issues/1854.


#### How to create a load balancer and do blue-green release

1. pushd terraform_load_balancer; terraform apply; popd

2. pushd ansible_load_balaner; ansible-playbook -i hosts --private-key=..terraform_load_balancer/load_balancer_rsa load_balancer.yml; popd;

The load balancer is an nginx server that proxies http requests to the
currently selected producer machine's 8002 port. If you want to
configure the ip and port of producer machine, go to load_balancer.yml
playbook and change the `nginx_backend_ip` and `nginx_backend_port`
variables.

If you want to seriously modify the nginx configuration, go to
`ansible_load_balancer/roles/ansible_load_balancer/templates/upstream.conf.js`
and modify it.


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
- https://alex.dzyoba.com/blog/terraform-ansible/ - how to generate Ansible inventory from Terraform
