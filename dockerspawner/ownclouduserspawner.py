import pwd
import shlex
import os
import shutil

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
        <label for="owncloud_username">Owncloud username:</label>
        <input
          id="username_inputs"
          type="username"
          autocapitalize="off"
          autocorrect="off"
          class="form-control"
          name="owncloud_username"
          value="{username}"
          tabindex="1"
        />

        <label for='owncloud_password'>Owncloud password:</label>
        <input
          id="password_input"
          type="password"
          class="form-control"
          name="owncloud_password"
          tabindex="2"
          autofocus="autofocus"
        />
        """.format( username = self.user.name )
    
    def options_from_form(self, formdata):
        options = {}
        options['username'] = ''
        options['password'] = ''
                
        arg = formdata.get('owncloud_username', [''])[0]
        if arg: options['username'] = arg
        arg = formdata.get('owncloud_password', [''])[0]
        if arg: options['password'] = arg
        
        self.davfs2_config = os.getenv('PWD') + '/.davfs2.%s' % self.user.name
        shutil.rmtree( self.davfs2_config, ignore_errors = True )
        os.mkdir( self.davfs2_config )
        f = open( self.davfs2_config + '/secrets', 'w' )
        f.write( 'https://tangshan.cosx-isinx.org/owncloud/remote.php/webdav %s %s\n' % ( options['username'], options['password'] ) )
        f.close()
        f = open( self.davfs2_config + '/davfs2.conf', 'w' )
        f.write( 'kernel_fs fuse\n' )
        f.write( 'use_locks 0\n' )
        f.write( 'table_size 65536\n' )
        f.write( 'dir_refresh 2\n' )
        f.write( 'delay_upload 1\n' )
        f.write( 'gui_optimize 1\n' )
        f.close()
        
        return options

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

    @property
    def volume_binds(self):
        """
        The second half of declaring a volume with docker-py happens when you
        actually call start().  The required format is a dict of dicts that
        looks like:

        {
            host_location: {'bind': container_location, 'ro': True}
        }
        """
        davfs2_config = 'davfs2.conf.%s' % self.user.name
        
        volumes = super(SystemUserSpawner, self).volume_binds
        volumes[ davfs2_config ] = {
            'bind': self.homedir + '/.davfs2/davfs2.conf',
            'ro': True
        }
        return volumes

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

        extra_create_kwargs['working_dir'] = '/cloud'

        if extra_host_config is None:
            extra_host_config = dict()
        extra_host_config[ 'privileged'] = True
        extra_host_config[ 'cap_add'   ] = [ 'SYS_ADMIN' ]
        extra_host_config[ 'devices'   ] = [ '/dev/fuse:/dev/fuse:rwm' ]
        
        print( self.user_options )

        return super(OwncloudUserSpawner, self).start(
            image=image,
            extra_create_kwargs=extra_create_kwargs,
            extra_start_kwargs=extra_start_kwargs,
            extra_host_config=extra_host_config
        )
