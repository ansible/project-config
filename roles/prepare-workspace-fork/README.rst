Prepare remote workspaces

This role is intended to run before any other role in a Zuul job.

It starts the Zuul console streamer on every host in the inventory,
and then copies the prepared source repos to the working directory on
every host.
