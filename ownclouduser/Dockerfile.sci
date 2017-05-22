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
    dnf reinstall -y glibc-common && \
    dnf install -y python3-matplotlib python3-scipy python3-scikit-learn && \
    dnf install -y pandoc && \
    dnf clean all

# re-install matplotlib to bring it to the latest version
# then install all pure-Python packages
RUN pip3 install --upgrade matplotlib && \
    pip3 install jupyterhub notebook && \
    pip3 install plotly ase && \
    rm -rf /root/.cache/pip/http

# install Python2 kernel
RUN dnf install -y gcc redhat-rpm-config python2-matplotlib python2-scipy python2-scikit-learn && \
    pip install ipython==5.3.0 && \
    pip install ipykernel && \
    python2 -m ipykernel install && \
    pip install --upgrade matplotlib && \
    dnf clean all && \
    rm -rf /root/.cache/pip/http

# IJulia must be installed after jupyter
RUN dnf install -y julia mbedtls-devel cmake czmq && \
    export JULIA_PKGDIR=/usr/local/share/julia/site && \
    julia -E 'Pkg.init(); Pkg.add("IJulia")' && \
    cp -r /usr/local/share/julia/site/v*/IJulia/deps/julia-* /usr/local/share/jupyter/kernels && \
    dnf clean all && \
    rm -rf /root/.cache/julia*

# TexLive for the 'download as PDF' option
RUN dnf install -y texlive-collection-xetex && \
    dnf install -y texlive-ec texlive-adjustbox texlive-upquote texlive-eurosym texlive-ucs texlive-palatino texlive-mathpazo && \
    dnf clean all

ADD usersetup.sh /usr/local/bin/start-usersetup.sh

CMD ["sh", "/usr/local/bin/start-usersetup.sh"]

