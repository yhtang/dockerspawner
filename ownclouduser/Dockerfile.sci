# Build as jupyterhub/ownclouduser
# Run with the DockerSpawner in JupyterHub

FROM docker.io/z620/fedora-docker-base-25-1.3.x86_64

MAINTAINER Yu-Hang Tang <yhtang@GitHub>

EXPOSE 8888

USER root
ENV SHELL /bin/bash
ENV LANG en_US.UTF-8
WORKDIR /root

RUN echo "deltarpm=0" >> /etc/dnf/dnf.conf
RUN dnf update -y && \
    dnf install -y sudo && \
    dnf install -y davfs2 && \
    dnf install -y langpacks-zh_CN langpacks-zh_TW langpacks-ja langpacks-ko && \
    dnf clean all

RUN pip3 install jupyterhub notebook && \
    pip3 install numpy scipy matplotlib plotly ase && \
    rm -rf /root/.cache/pip/http

ADD usersetup.sh /usr/local/bin/start-usersetup.sh

CMD ["sh", "/usr/local/bin/start-usersetup.sh"]

