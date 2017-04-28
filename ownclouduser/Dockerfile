# Build as jupyterhub/ownclouduser
# Run with the DockerSpawner in JupyterHub

FROM jupyter/minimal-notebook
# FROM jupyterhub/singleuser

MAINTAINER Yu-Hang Tang <yhtang@GitHub>

USER root

WORKDIR /home
RUN userdel jovyan && rm -rf /home/jovyan
ENV SHELL /bin/bash

ADD usersetup.sh /usr/local/bin/start-usersetup.sh

# smoke test entrypoint
RUN USER=octest sh /usr/local/bin/start-usersetup.sh -h && userdel -r octest

CMD ["sh", "/usr/local/bin/start-usersetup.sh"]
