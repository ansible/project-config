#!/usr/bin/env python

# Copyright 2017 SUSE Linux GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import sys
import yaml

github_yaml = 'github/projects.yaml'
github_projects = yaml.safe_load(open(github_yaml))
projects_yaml = 'zuul.d/projects.yaml'
projects = yaml.safe_load(open(projects_yaml))


def normalize(s):
    "Normalize string for comparison."
    return s.lower().replace("_", "-")


def check_projects_sorted():
    """Check that the projects are in alphabetical order per section."""

    print("\n➜ Checking project list for alphabetical order")

    errors = False
    last = ""
    for entry in projects:
        current = entry['project']['name']
        if (normalize(last) > normalize(current)):
            print("  ERROR: Wrong alphabetical order: %(last)s, %(current)s" %
                  {"last": last, "current": current})
            errors = True
        last = current

    if not errors:
        print("... all fine.")
    return errors


def check_projects_default_branch_with_gh():
    """Check the project default-branches are in sync with Github."""

    print("\n➜ Checking if Github and local default-branch config is consist")

    errors = False
    gh_token_file = "github_token_file.txt"
    try:
        with open(gh_token_file) as fh:
            gh_auth_login = ["gh", "auth", "login", "--with-token"]
            subprocess.check_call(gh_auth_login, stdin=fh)
    except FileNotFoundError:
        print("  WARNING: gh command not available. skipping the check")
        return errors
    except subprocess.CalledProcessError:
        print("  WARNING: gh auth login failed, skipping the check")
        return errors
    except Exception as e:
        print("  WARNING: gh auth login error: {}".format(e))
        return errors

    try:
        subprocess.check_call(["gh", "auth", "status"])
    except FileNotFoundError:
        print("  WARNING: gh command not available. skipping the check")
        return errors
    except subprocess.CalledProcessError:
        print("  WARNING: gh command is not configured, "
              "skipping the check")
        return errors

    for entry in projects:
        current = entry["project"]["name"]
        if not current.startswith("github.com/"):
            continue
        expected_branch = entry["project"].get("default-branch", "master")
        gh_repo = current[11:]
        real_default_branch = subprocess.check_output(
            [
                "gh",
                "repo",
                "view",
                gh_repo,
                "--json",
                "defaultBranchRef",
                "--jq",
                ".defaultBranchRef.name",
            ],
            text=True,
        ).rstrip()
        if real_default_branch != expected_branch:
            print(
                f"  ERROR: Repo {current}'s default-branch should "
                f"be {real_default_branch}"
            )
            errors = True
    if not errors:
        print("... all fine.")
    return errors


def check_projects_default_branch():
    """Check that the projects default-branch is in sync."""

    print("\n➜ Checking local default-branch consistency")

    errors = False
    for gh in github_projects:
        for entry in projects:
            current = entry["project"]["name"]
            if "github.com/" + gh["project"] == current:
                github_default_branch = gh.get("default-branch")
                zuul_default_branch = entry["project"].get("default-branch")
                if github_default_branch != zuul_default_branch:
                    print(
                        f"  ERROR: Wrong default-branch for {current} "
                        f"{github_default_branch} in github/projects.yaml vs "
                        f"{zuul_default_branch} in zuul.d/projects.yaml "
                    )
                    errors = True
                break

    if not errors:
        print("... all fine.")
    return errors


def check_release_jobs():
    """Minimal release job checks."""

    release_templates = []

    errors = False
    print("\n➜ Checking release jobs")
    for entry in projects:
        project = entry['project']
        name = project['name']
        found = [tmpl for tmpl in project.get('templates', [])
                 if tmpl in release_templates]
        if len(found) > 1:
            errors = True
            print("  ERROR: Found multiple release jobs for %s:" % name)
            for x in found:
                print("    %s" % x)
            print("  Use only one of them.")

    if not errors:
        print("... all fine.")
    return errors


def blacklist_jobs():
    """Check that certain jobs and templates are *not* used."""

    # Currently only handles templates
    blacklist_templates = []

    errors = False
    print("\n➜ Checking for obsolete jobs and templates")
    for entry in projects:
        project = entry['project']
        name = project['name']
        found = [tmpl for tmpl in project.get('templates', [])
                 if tmpl in blacklist_templates]
        if found:
            errors = True
            print("  ERROR: Found obsolete template for %s:" % name)
            for x in found:
                print("    %s" % x)
            print("  Remove it.")

    if not errors:
        print("... all fine.")
    return errors


def check_pipeline(project, job_pipeline, pipeline_name):
    errors = False

    for job in job_pipeline:
        if isinstance(job, dict):
            for name in job:
                if ('voting' in job[name] and
                        (not job[name]['voting'])):
                    errors = True
                    print("  Found non-voting job in %s:" % pipeline_name)
                    print("    project: %s" % project['name'])
                    print("    job: %s" % name)
    return errors


def check_pipelines(project, pipeline_name):
    errors = False

    if pipeline_name in project and 'jobs' in project[pipeline_name]:
        errors = check_pipeline(project, project[pipeline_name]['jobs'],
                                pipeline_name)
    return errors


def check_voting():
    errors = False
    print("\n➜ Checking voting status of jobs")

    for entry in projects:
        project = entry['project']
        errors |= check_pipelines(project, 'gate')
        errors |= check_pipelines(project, 'periodic')
        errors |= check_pipelines(project, 'periodic-1hr')
        errors |= check_pipelines(project, 'post')
        errors |= check_pipelines(project, 'promote')

    if errors:
        print(" Note the following about non-voting jobs in pipelines:")
        print(" * Never run non-voting jobs in gate pipeline, they just")
        print("   waste resources, remove such jobs.")
        print(" * Experimental, periodic, and post pipelines are always")
        print("   non-voting. The 'voting: false' line is redundant, remove")
        print("   it.")
    else:
        print("... all fine.")
    return errors


def check_only_boilerplate():
    """Check for redundant boilerplate with not jobs."""

    errors = False
    print("\n➜ Checking that every project has entries")
    for entry in projects:
        project = entry['project']
        if len(project.keys()) <= 1:
            name = project['name']
            errors = True
            print("  Found project %s with no jobs configured." % name)

    if errors:
        print("Errors found!\n")
        print("Do not add projects with only names entry but no jobs,")
        print("remove the entry completely - unless you forgot to add jobs.")
    else:
        print("... all fine.")

    return errors


def check_all():

    errors = check_projects_sorted()
    errors = check_projects_default_branch_with_gh() or errors
    errors = check_projects_default_branch() or errors
    errors = blacklist_jobs() or errors
    errors = check_release_jobs() or errors
    errors = check_voting() or errors
    errors = check_only_boilerplate() or errors

    if errors:
        print("\nFound errors in zuul.d/projects.yaml!\n")
    else:
        print("\nNo errors found in zuul.d/projects.yaml!\n")
    return errors


if __name__ == "__main__":
    sys.exit(check_all())
