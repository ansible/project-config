Generate and install a build-local SSH key on all hosts

This role is intended to be run on the Zuul Executor at the start of
every job.  It generates an SSH keypair and installs the public key in
the authorized_keys file of every host in the inventory.  It then
removes the Zuul master key from this job's SSH agent so that the
original key used to log into all of the hosts is no longer accessible
(any per-project keys, if present, remain available), then adds the
newly generated private key.

**Role Variables**

.. zuul:rolevar:: zuul_temp_ssh_key
   :default: ``{{ zuul.executor.work_root }}/{{ zuul.build }}_id_rsa``

   Where to put the newly-generated SSH private key.

.. zuul:rolevar:: zuul_ssh_key_dest
   :default: id_rsa

   File name for the the newly-generated SSH private key.

.. zuul:rolevar:: zuul_build_sshkey_cleanup
   :default: false

   Remove previous build sshkey. Set it to true for single use static node.
   Do not set it to true for multi-slot static nodes as it removes the
   build key configured by other jobs.

.. zuul:rolevar:: zuul_ssh_key_algorithm
   :default: rsa

   The digital signature algorithm to be used to generate the key. Default value
   'rsa'.

.. zuul:rolevar:: zuul_ssh_key_size
   :default: 3072

   Specifies the number of bits in the key to create. The default length is
   3072 bits (RSA).
