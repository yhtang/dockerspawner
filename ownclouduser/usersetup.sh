#!/bin/sh
set -e
export UNIQUE_USER=$USER
while getent passwd $UNIQUE_USER > /dev/null ; do
  echo "$UNIQUE_USER exists"
  export UNIQUE_USER=$USER$RANDOM
  echo "Trying $UNIQUE_USER"
done

echo "Creating user $UNIQUE_USER"
useradd -u 9999 -s $SHELL --home-dir=/home/$UNIQUE_USER --create-home $UNIQUE_USER
# chown $UNIQUE_USER:$UNIQUE_USER /home/$UNIQUE_USER

# TODO: install davfs2 and mount owncloud

notebook_arg=""
if [ -n "${NOTEBOOK_DIR:+x}" ]
then
    notebook_arg="--notebook-dir=${NOTEBOOK_DIR}"
fi

sudo -E PATH="${CONDA_DIR}/bin:$PATH" -u $UNIQUE_USER $CONDA_DIR/bin/jupyterhub-singleuser \
  --port=8888 \
  --ip=0.0.0.0 \
  --user=$JPY_USER \
  --cookie-name=$JPY_COOKIE_NAME \
  --base-url=$JPY_BASE_URL \
  --hub-prefix=$JPY_HUB_PREFIX \
  --hub-api-url=$JPY_HUB_API_URL \
  ${notebook_arg} \
  $@
