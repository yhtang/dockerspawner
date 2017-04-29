# Build as jupyterhub/ownclouduser
# Run with the DockerSpawner in JupyterHub

FROM docker.io/z620/fedora-docker-base-25-1.3.x86_64

MAINTAINER Yu-Hang Tang <yhtang@GitHub>

EXPOSE 8888

USER root
ENV SHELL /bin/bash
WORKDIR /root

RUN echo "deltarpm=0" >> /etc/dnf/dnf.conf
RUN dnf update -y && dnf install -y sudo davfs2 && dnf clean all

RUN pip3 install jupyterhub notebook && rm -rf /root/.cache/pip/http

ADD usersetup.sh /usr/local/bin/start-usersetup.sh

# smoke test entrypoint
RUN USER=octest sh /usr/local/bin/start-usersetup.sh -h && userdel -r octest

CMD ["sh", "/usr/local/bin/start-usersetup.sh"]
