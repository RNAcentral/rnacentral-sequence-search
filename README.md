# RNAcentral Sequence Search DevOps code

This repository contains DevOps code for managing the [RNAcentral](https://rnacentral.org) sequence search
microservice infrastructure.

## Installation

There are 3 environments:

 - **docker-compose**
    to start up the database, producer, and consumer for local development
    using `docker-compose up`.

 - **local**
     when developing new features, both producer and consumer are
     supposed to be run from local machine and postgres database server
     is also meant to be run on localhost:5432

 - **production**
    this is the production cloud environment, where the code is deployed to openstack

There is also a _test_ environment that is not currently documented. It is used for
running unit-tests on local machine only, it is not using any database or network communications.

### Manual deployment in production

**Requirements**

- [Terraform](https://www.terraform.io)
- [Terraform inventory](https://github.com/adammck/terraform-inventory)
- [Virtual environment](https://virtualenv.pypa.io/en/latest/) with installed dependencies
- [Memcached](https://memcached.org/)

1. Create `terraform/providers.tf` using the `providers.tf.template` file.

2. Generate `sequence_search_rsa` key:

  `cd terraform && ssh-keygen -t rsa -b 4096`

  See: https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

3. Follow steps in `redeploy.jenkinsfile`.

  - Install SSH keys
  - Run `terraform init && terraform apply` to create the infrastructure
  - Run ansible to create postgres database
  - Run ansible to create producer instance
  - Run ansible to create consumer instances

### Development workflow

1. Choose terraform workspace:

    `terraform workspace select <env>` where `env` can be `default` or `test`.
    Once the workspace is selected, terraform will choose the correct `tfstate`
    file and will know how to configure ssh keys.

2. Run `terraform apply`.

    This will check that the infrastructure is up and running, configure ssh keys,
    and update ansible inventory on each run.

3. To apply python or ansible changes, run the appropriate ansible playbook:

    `ansible-playbook -i hosts ...`

---------------------------

### Additional notes

#### How to upload image with databases to openstack

1. Create an .iso image from `databases` folder on Mac:

 `cd sequence_search/consumer`
 `hdiutil makehybrid -o databases.iso databases -iso -joliet`

2. To upload image to the cloud first download `openstack.rc` (v2) from Horizon dashboard

3. Source it: `source openstack.rc`, enter your user's password

4. Create a glance image:

 `glance image-create --name sequence_search_databases --disk-format=iso --container-format=bare --file databases.iso`

See: https://matt.berther.io/2008/12/14/creating-iso-images-from-a-folder-in-osx/

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

`pushd ansible;  ...`


#### Frontend

The embedded component is being used as frontend code. It is not needed in production, but it can be useful for testing.

The code is available here: https://github.com/RNAcentral/rnacentral-sequence-search-embed


#### Using terraform workspaces for blue-green release

1. Choose a workspace: `terraform workspace select <environment>`

  Environment can be `default` or `test`. Al subsequent terraform commands
  will apply only to that environment.

2. Apply terraform changes: `terraform apply`

  The `main.tf` will automatically configure the correct IP depending on the workspace.

3. Update local ssh config: `ansible-playbook -i hosts localhost.yml`

  The IP address will be set depending on the current `terraform.tfstate` which
  is enabled by the terraform workspace.

4. Run any other ansible playbooks: `ansible-playbook -i hosts producer.yml`


#### How to create a load balancer and do blue-green release

1. `pushd terraform_load_balancer; terraform apply; popd`

2. Run the command bellow passing the IPs as variables on the command line:

    ```
    cd ansible_load_balancer
    ansible-playbook -i hosts --private-key=../terraform_load_balancer/load_balancer_rsa --extra-vars "main_ip=main.ip.address fallback_ip=fallback.ip.address" load_balancer.yml
    ```

The load balancer is an nginx server that proxies http requests to the currently selected producer machine's `8002` 
port. If you want to change the port of producer machine, go to `load_balancer.yml` playbook and change the 
`nginx_backend_port` variable.

If you want to update nginx configuration, make changes in
`ansible_load_balancer/roles/ansible_load_balancer/templates/upstream.conf.js`.

#### Installation in production using Jenkins

To configure Jenkins deployment:

- Install and configure Jenkins
- In Jenkins interface create a one-branch pipeline for each `*.jenkinsfile` in `/jenkins` folder
- In Jenkins upload secret file `openstack.rc` copied from RedHat Horizon dashboard
 (Project -> Compute -> Access & Security -> API Access)
- Install python-based dependencies via `pip install -r requirements.txt` (possibly, using a virtualenv)

#### Manual installation in local environment

1. `git clone https://github.com/RNAcentral/rnacentral-sequence-search.git`
2. `cd rnacentral-sequence-search`
3. `virtualenv ENV --python=python3`
4. `source ENV/bin/activate`
5. `pip3 install -r sequence_search/requirements.txt`
6. `pushd sequence_search/consumer`
7. `curl -OL http://eddylab.org/software/hmmer/hmmer-3.2.1.tar.gz && \
    tar -zxvf hmmer-3.2.1.tar.gz && \
    cd hmmer-3.2.1 && \
    ./configure --prefix /usr/local && \
    make && \
    make install && \
    cd easel; make install && \
    cd ../../`
8. `curl -OL http://eddylab.org/infernal/infernal-1.1.3.tar.gz && \
    tar xf infernal-1.1.3.tar.gz && \
    cd infernal-1.1.3 && \
    ./configure --prefix /usr/local && \
    make && \
    make install && \
    cd ../`
9. `mkdir rfam && \
    cd rfam && \
    curl -OL ftp://ftp.ebi.ac.uk/pub/databases/Rfam/CURRENT/Rfam.cm.gz && \
    gunzip Rfam.cm.gz && \
    cmpress Rfam.cm && \
    cd ../`
10. `git clone https://github.com/nawrockie/cmsearch_tblout_deoverlap.git`    
11. `rsync <database/fasta/files/location/on/local/machine> databases/` - copy `.fasta` files with databases we want to search against into `sequence_search/consumer/databases folder`
12. If necessary, update the contents of `sequence_search/consumer/rnacentral_database.py` accordingly (there's a mapping of database human-readable names to file names).
13. `popd`
14. `pushd sequence_search/producer/static`
15. `git clone https://github.com/RNAcentral/rnacentral-sequence-search-embed.git && \
     cd rnacentral-sequence-search-embed && \
     git checkout localhost`
16. `popd`
17. Edit `postgres/local_init.sql` file and replace role `apetrov` there with your username on local machine
18. Edit `sequence_search/db/settings.py` and replace role `apetrov` with your username on local machine
19. `docker build -t local-postgres -f postgres/local.Dockerfile postgres` - this will create an image with postgres databases.
20. `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -t local-postgres` - this will create and start an instance of postgres on your local machine's 5432 port.
21. `python3 -m sequence_search.db` - creates necessary database tables for producer and consumer to run
22. `python3 -m sequence_search.producer` - starts producer server on port 8002
23. `python3 -m sequence_search.consumer` - starts consumer server on port 8000
24. `brew install memcached` - install memcached using Homebrew
25. `memcached` - start memcached server

### Sources of inspiration

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
