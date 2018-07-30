# Non-coding RNA Sequence Search Repository DevOps code

This repository contains DevOps code for managing a non-coding RNA Sequence Search microservice infrastructure.

Basically, it provides a set of Jenkinsfiles for managing Sequence Search infrastructure as a
Kubernetes cluster on top of EBI OpenStack. Internally those Jenkinsfiles rely upon a set of bash scripts,
Ansible playbooks and OpenStack console client commands.

Unfortunately, Red Hat OpenStack doesn't support the Magnum API that allows for provisioning a Kubernetes
clusters from the console. Thus, we had to resort to Kubespray scipts.


## How to use this

### Installation

Suppose that you want to install this set of Jenkins pipelines to an entirely new machine.

Here are the steps required to do this:

- Install and configure Jenkins on that machine
- In Jenkins interface create a one-branch pipeline for each `*.jenkinsfile` in `/jenkins` folder
- In Jenkins upload secret file `openstack.rc` copied from RedHat Horizon dashboard
 (Project -> Compute -> Access & Security -> API Access)
- Install python-based dependencies via `pip install -r requirements.txt` (possibly, using a virtualenv)


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
