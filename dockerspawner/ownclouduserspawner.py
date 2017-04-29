import pwd
import shlex

from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)

class OwncloudUserSpawner(DockerSpawner):

    container_image = Unicode("jupyterhub/ownclouduser", config=True)

    def _options_form_default(self):
       return """
        <label for="owncloud_username">Owncloud Username:</label>
        <input
          id="username_input"
          type="username"
          autocapitalize="off"
          autocorrect="off"
          class="form-control"
          name="username"
          val="{{username}}"
          tabindex="1"
          autofocus="autofocus"
        />

        <label for='owncloud_password'>Owncloud password:</label>
        <input
          type="password"
          class="form-control"
          name="password"
          id="owncloud_password"
          tabindex="2"
        />
        """.format( username = self.user.name )
    
    def options_from_form(self, formdata):
        options = {}
        options['env'] = env = {}
        
        env_lines = formdata.get('env', [''])
        for line in env_lines[0].splitlines():
            if line:
                key, value = line.split('=', 1)
                env[key.strip()] = value.strip()
        
        arg_s = formdata.get('args', [''])[0].strip()
        if arg_s:
            options['argv'] = shlex.split(arg_s)
        return options
    
    def get_args(self):
        """Return arguments to pass to the notebook server"""
        argv = super().get_args()
        if self.user_options.get('argv'):
            argv.extend(self.user_options['argv'])
        return argv
    
    def get_env(self):
        env = super().get_env()
        if self.user_options.get('env'):
            env.update(self.user_options['env'])
        return env

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

        if extra_host_config is None:
            extra_host_config = dict()
        extra_host_config[ 'privileged'] = True
        extra_host_config[ 'cap_add'   ] = [ 'SYS_ADMIN' ]
        extra_host_config[ 'devices'   ] = [ '/dev/fuse:/dev/fuse:rwm' ]

        return super(OwncloudUserSpawner, self).start(
            image=image,
            extra_create_kwargs=extra_create_kwargs,
            extra_start_kwargs=extra_start_kwargs,
            extra_host_config=extra_host_config
        )
