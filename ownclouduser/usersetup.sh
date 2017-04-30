#!/bin/sh
set -e

if getent passwd $USER > /dev/null ; then
  echo "$USER exists"
else
  echo "Creating user $USER"
  useradd -u 9999 -s $SHELL --home-dir=/home/$USER $USER
fi

if [ ! -d /home/$USER ]; then
  echo "Creating home folder for $USER at /home"
  mkdir /home/$USER
fi
echo "Set ownership of /home/$USER to $USER:$USER"
chown $USER:$USER /home/$USER

# use davfs2 to mount ownCloud
echo "Configure /etc/davfs2 ownership"
chown -R root:root /etc/davfs2
chmod 700 /etc/davfs2
chmod 600 /etc/davfs2/*
CLOUD_DIR=/cloud
if [ $(df | grep "/cloud" | wc -l) -gt 0 ]; then
  echo "Unmount previously mounted /cloud"
  umount /cloud
fi
echo "Mount /cloud"
mount -t davfs https://tangshan.cosx-isinx.org/owncloud/remote.php/webdav -o user,rw,auto,uid=$USER,gid=$USER $CLOUD_DIR

echo "Launch notebook"
sudo -E -u $USER jupyterhub-singleuser \
  --port=8888 \
  --ip=0.0.0.0 \
  --user=$JPY_USER \
  --cookie-name=$JPY_COOKIE_NAME \
  --base-url=$JPY_BASE_URL \
  --hub-prefix=$JPY_HUB_PREFIX \
  --hub-api-url=$JPY_HUB_API_URL \
  --notebook-dir=$CLOUD_DIR \
  $@
