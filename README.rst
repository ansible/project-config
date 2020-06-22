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

Add to [zuul/tenants.yaml](https://github.com/ansible/project-config/blob/master/zuul/tenants.yaml)

PR2
---

Add to [zuul.d/projects.yaml](https://github.com/ansible/project-config/blob/master/zuul.d/projects.yaml)

Status
======

[Zuul Dashboard](https://dashboard.zuul.ansible.com/t/ansible/status)

Talk to us
==========

Freenode `#ansible-zuul`
