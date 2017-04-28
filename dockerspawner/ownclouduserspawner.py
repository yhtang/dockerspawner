import pwd

from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)

class OwncloudUserSpawner(DockerSpawner):

    container_image = Unicode("jupyterhub/ownclouduser", config=True)

    image_homedir_format_string = Unicode(
        "/home/{username}",
        config=True,
        help=dedent(
            """
            Format string for the path to the user's home directory
            inside the image.  The format string should include a
            `username` variable, which will be formatted with the
            user's username.
            """
        )
    )

    user_id = Integer(9999,
        help=dedent(
            """
            User id is irrelevant if we are mounting from the owncloud WebDAV interface
            """
        )
    )

    @property
    def homedir(self):
        """
        Path to the user's home directory in the docker image.
        """
        return self.image_homedir_format_string.format(username=self.user.name)

    def get_env(self):
        env = super(OwncloudUserSpawner, self).get_env()
        env.update(dict(
            USER=self.user.name,
            USER_ID=self.user_id,
            HOME=self.homedir
        ))
        return env
    
    def _user_id_default(self):
        return 9999

    def load_state(self, state):
        super().load_state(state)
        if 'user_id' in state:
            self.user_id = state['user_id']

    def get_state(self):
        state = super().get_state()
        if self.user_id >= 0:
            state['user_id'] = self.user_id
        return state

    def start(self, image=None, extra_create_kwargs=None,
        extra_start_kwargs=None, extra_host_config=None):
        """start the single-user server in a docker container"""
        if extra_create_kwargs is None:
            extra_create_kwargs = {}

        if 'working_dir' not in extra_create_kwargs:
            extra_create_kwargs['working_dir'] = self.homedir

        extra_host_config[ 'privileged'] = True
        extra_host_config[ 'cap_add'   ] = [ 'SYS_ADMIN' ]
        extra_host_config[ 'device'    ] = [ '/dev/fuse:/dev/fuse:rwm' ]

        return super(OwncloudUserSpawner, self).start(
            image=image,
            extra_create_kwargs=extra_create_kwargs,
            extra_start_kwargs=extra_start_kwargs,
            extra_host_config=extra_host_config
        )
