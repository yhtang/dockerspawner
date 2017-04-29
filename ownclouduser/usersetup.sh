#!/bin/sh
set -e

if getent passwd $USER > /dev/null ; do
  echo "$USER exists"
else
  echo "Creating user $USER"
  useradd -u 9999 -s $SHELL --home-dir=/home/$USER $USER
done

if [ ! -d /home/$USER ]; then
  mkdir /home/$USER
fi
chown -R $USER:$USER /home/$USER

# TODO: install davfs2 and mount owncloud

notebook_arg=""
if [ -n "${NOTEBOOK_DIR:+x}" ]
then
    notebook_arg="--notebook-dir=${NOTEBOOK_DIR}"
fi

sudo -E -u $USER jupyterhub-singleuser \
  --port=8888 \
  --ip=0.0.0.0 \
  --user=$JPY_USER \
  --cookie-name=$JPY_COOKIE_NAME \
  --base-url=$JPY_BASE_URL \
  --hub-prefix=$JPY_HUB_PREFIX \
  --hub-api-url=$JPY_HUB_API_URL \
  ${notebook_arg} \
  $@
