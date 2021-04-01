project-config
==============

This repo contains a set of config files that are consumed by the
ansible-network/windmill-config playbooks in order to deploy and configure
our Zuul Infrastructure.

zuul
====

This directory contains the tenant configuration for zuul.ansible.com. Edit
these files to add, remove or rename a project in Zuul.

On-board new repo into Zuul
===========================

To add new repos into Zuul, it's a two step process:

PR1
---

- Add to `zuul/tenants.yaml <https://github.com/ansible/project-config/blob/master/zuul/tenants.yaml>`_

note: Follow up to the merge of the PR, Zuul will refresh it's configuration. The job is called `windmill-config-deploy`. For various reason, the update may fail, you can take a look at the previous runs here: https://dashboard.zuul.ansible.com/t/ansible/builds?job_name=windmill-config-deploy

PR2
---

- Add to `zuul.d/projects.yaml <https://github.com/ansible/project-config/blob/master/zuul.d/projects.yaml>`_
- Add to `github/acls <https://github.com/ansible/project-config/tree/master/github/acls>`_
- Add to `github/projects.yaml <https://github.com/ansible/project-config/blob/master/github/projects.yaml>`_

Status
======

`Zuul Dashboard <https://dashboard.zuul.ansible.com/t/ansible/status>`_

Talk to us
==========

Freenode ``#ansible-zuul``
