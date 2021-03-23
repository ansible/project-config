gitops for github
=================

The purpose of this folder is to move all github admin actions into #gitops tasks controlled via pull request.  We do this to remove the need for all the humans to have admin access to github namespaces.

Creating a new repo
-------------------

If you would like to create a new repo in github, you first need to add your project to the ```projects.yaml``` file in this directory. There is an example of the stanza used at the top of the file.

Adding branch projection
------------------------

Once the project has been added to the ```projects.yaml``` file, it is highly recommended you also include your branch protection configuration. This is done by placing a file into the ```acls``` directory, then namespace, followed by repo name (dot) config.  You can see an example of the format by looking at ```acls\ansible-network\sandbox.config```.
