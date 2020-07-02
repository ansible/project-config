#! /usr/bin/env python
# Copyright (C) 2011 OpenStack, LLC.
# Copyright (c) 2012 Hewlett-Packard Development Company, L.P.
# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import configparser
import logging
import os
import yaml

import github

LOG = logging.getLogger(__name__)


class Client(object):

    def load_projects(self):
        return yaml.safe_load(open(self.args.projects))

    def parse_arguments(self):
        parser = argparse.ArgumentParser(
            description='manage projects')
        parser.add_argument(
            '--config-file', dest='config',
            default='~/.github-projects.config',
            help='path to github-projects.config'),
        parser.add_argument(
            '-p', dest='projects',
            default='github/projects.yaml',
            help='path to projects.yaml file')
        parser.add_argument(
            '--debug', dest='debug', action='store_true',
            help='Print debugging output (set logging level to DEBUG instead '
            ' of default INFO level)')

        self.args = parser.parse_args()

    def process_projects(self):
        projects = self.load_projects()
        gh = github.Github(self.config.get('github', 'token'))
        orgs = gh.get_user().get_orgs()
        orgs_dict = dict(zip([o.login.lower() for o in orgs], orgs))

        for item in projects:
            LOG.info('Processing project: %s' % item['project'])
            self._process_project(item, orgs_dict)

    def _process_project(self, item, orgs_dict):
        project_split = item['project'].split('/', 1)
        org_name = project_split[0]
        repo_name = project_split[1]

        kwargs = {
            'allow_merge_commit': True,
            'allow_rebase_merge': False,
            'allow_squash_merge': True,
            'description': item.get('description', None),
        }
        options = item.get('options', [])
        kwargs['has_downloads'] = 'has-downloads' in options or False
        kwargs['has_issues'] = 'has-issues' in options or True
        kwargs['has_projects'] = 'has-projects' in options or False
        kwargs['has_wiki'] = 'has-wiki' in options or False

        try:
            org = orgs_dict[org_name.lower()]
        except KeyError as e:
            LOG.exception(e)
            raise

        try:
            LOG.info('Fetching github repository info about %s', repo_name)
            repo = org.get_repo(repo_name)
        except github.GithubException:
            # NOTE(pabelanger): We should also allow to import an existing
            # project from upstream source.
            kwargs['auto_init'] = True
            LOG.info(
                'Creating %s in github', repo_name)
            repo = org.create_repo(
                name=repo_name, **kwargs)
            return

        # TODO(pabelanger): Currently github doesn't expose a way to auto init
        # a repo to a branch other then master.
        kwargs['default_branch'] = item.get('default-branch', 'master')

        if repo.archived:
            # Repo is archived, we cannot update it.
            return

        if kwargs['allow_merge_commit'] == repo.allow_merge_commit:
            del kwargs['allow_merge_commit']
        if kwargs['allow_rebase_merge'] == repo.allow_rebase_merge:
            del kwargs['allow_rebase_merge']
        if kwargs['allow_squash_merge'] == repo.allow_squash_merge:
            del kwargs['allow_squash_merge']
        if kwargs['default_branch'] == repo.default_branch:
            del kwargs['default_branch']
        if kwargs['description'] == repo.description:
            del kwargs['description']
        if kwargs['has_downloads'] == repo.has_downloads:
            del kwargs['has_downloads']
        if kwargs['has_issues'] == repo.has_issues:
            del kwargs['has_issues']
        if kwargs['has_projects'] == repo.has_projects:
            del kwargs['has_projects']
        if kwargs['has_wiki'] == repo.has_wiki:
            del kwargs['has_wiki']
        if item.get('archived', False):
            kwargs['archived'] = True

        if kwargs:
            LOG.info("Updating %s in github", repo_name)
            repo.edit(repo_name, **kwargs)

        acl_config = '%s.config' % os.path.join('acls', item['project'])

        if acl_config:
            dirname = (os.path.dirname(os.path.abspath(self.args.projects)))
            acl_config = os.path.join(dirname, acl_config)
            self.process_acls(acl_config, repo)

    def process_acls(self, acl_config, repo):
        if not os.path.isfile(acl_config):
            return

        config = yaml.safe_load(open(acl_config))
        for entry in config:
            branch_name = entry['name']

            kwargs = {
                'enforce_admins': entry.get('enforce_admins', False),
            }

            _status_checks = entry.get('required_status_checks', [])
            if 'contexts' in _status_checks:
                kwargs['contexts'] = _status_checks.get('contexts')

            LOG.info('Fetching github branch info about %s', repo.name)
            branch = repo.get_branch(branch_name)
            try:
                branch_p = branch.get_protection()

                if kwargs['enforce_admins'] == branch_p.enforce_admins:
                    del kwargs['enforce_admins']
                _checks = branch_p.required_status_checks
                if _checks and kwargs['contexts'] == _checks.contexts:
                    del kwargs['contexts']
            except github.GithubException:
                # There is no branch protection rule to compare existing
                # settings. Create the rule will all settings.
                pass

            if kwargs:
                LOG.info("Updating branch protection rule for %s", branch_name)
                branch.edit_protection(**kwargs)

    def read_config(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.expanduser(self.args.config))

    def setup_logging(self):
        if self.args.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def main(self):
        self.parse_arguments()
        self.setup_logging()
        self.read_config()
        self.process_projects()


def main():
    Client().main()


if __name__ == "__main__":
    main()
