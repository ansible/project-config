Log a few lines about the job.

**Role Variables**

.. zuul:rolevar:: zuul_log_url

   Base URL where logs are to be found.

.. zuul:rolevar:: zuul_log_path_shard_build
   :default: False

   This var is consumed by set-zuul-log-path-fact which emit-job-header
   calls into. If you set this you will get log paths prefixed with the
   first three characters of the build uuid. This will improve log file
   sharding.

   More details can be found at :zuul:rolevar:`set-zuul-log-path-fact.zuul_log_path_shard_build`
