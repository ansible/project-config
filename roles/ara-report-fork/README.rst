If ARA is enabled, generates a report or saves a copy of the ARA database.

**Role Variables**

.. zuul:rolevar:: ara_report_run
   :default: ``true``

   Whether to run this role or not.
   Possible values:

   - ``true`` (always run)
   - ``false`` (never run)
   - ``failure`` (only run when there has been a failure)

.. zuul:rolevar:: ara_database_path
   :default: ``{{ zuul.executor.work_root }}/.ara/ansible.sqlite``

   Absolute path where the ARA database is expected on the control node.
   This should be where the ansible-playbook execution had ARA save the host,
   task and result data if you provided a custom location through
   ``ARA_DATABASE`` or an ``ansible.cfg`` file.

.. zuul:rolevar:: ara_report_type
   :default: ``html``

   Possible values:

   - ``html``
   - ``database``

   ``html`` will have ARA generate and save a statically generated HTML report
   inside ``ara_report_path``.

   ``database`` will only save the raw ARA sqlite database inside
   ``ara_report_path``. The database can then be downloaded by users or loaded
   dynamically by the ``ara-wsgi-sqlite`` middleware.

   See the `ARA documentation`_ for details.

.. _ARA documentation: https://ara.readthedocs.io/en/latest/advanced.html

.. zuul:rolevar:: ara_compress_html
   :default: ``true``

   When report_type is 'html', whether to compress the ARA HTML output or not.

.. tip::
   Make sure the web server is configured to set the required mimetypes_ in
   order to serve gzipped content properly.

.. _mimetypes: https://git.openstack.org/cgit/openstack-infra/puppet-openstackci/tree/templates/logs.vhost.erb?id=5fe1f3d2d5e40c2458721e7dcf8631d62ea2525f#n24

.. zuul:rolevar:: ara_report_path
   :default: ``ara``

   This path is relative to the root of the log directory.

   When report_type is 'html' directory where the HTML report will be generated.
   When report_type is 'database', directory where the database is saved.

.. zuul:rolevar:: ara_report_executable
   :default: ``ara``

   Path to ara executable.
