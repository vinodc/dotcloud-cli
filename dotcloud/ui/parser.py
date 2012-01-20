import argparse
from .version import VERSION

def get_parser(name='dotcloud'):
    parser = argparse.ArgumentParser(prog=name, description='dotcloud CLI')
    parser.add_argument('--application', '-A', help='specify the application')
    parser.add_argument('--environment', '-E', help='specify the environment')
    parser.add_argument('--version', '-v', action='version', version='dotcloud/{0}'.format(VERSION))
    parser.add_argument('--trace', action='store_true', help='Display trace ID')
    
    subcmd = parser.add_subparsers(dest='cmd')

    subcmd.add_parser('list', help='list applications')
    subcmd.add_parser('version', help='show version')

    check = subcmd.add_parser('check', help='Check the installation and authentication')
    setup = subcmd.add_parser('setup', help='Setup the client authentication')

    create = subcmd.add_parser('create', help='Create a new application')
    create.add_argument('application', help='specify the application')

    conn = subcmd.add_parser('connect', help='Connect a local directory with an existing app')
    conn.add_argument('application', help='specify the application')

    destroy = subcmd.add_parser('destroy', help='Destroy an existing app')
    destroy.add_argument('service', nargs='?', help='Specify the service')

    disconnect = subcmd.add_parser('disconnect', help='Disconnect the current directory from DotCloud app')

    app = subcmd.add_parser('app', help='Show the application name linked to the current directory')

    info = subcmd.add_parser('info', help='Get information about the application')
    info.add_argument('service', nargs='?', help='Specify the service')

    url = subcmd.add_parser('url', help='Show URL for the application')
    url.add_argument('service', nargs='?', help='Specify the service')

    ssh = subcmd.add_parser('ssh', help='SSH into the service')
    ssh.add_argument('service', help='Specify the service')

    run = subcmd.add_parser('run', help='SSH into the service')
    run.add_argument('service', help='Specify the service')
    run.add_argument('command', nargs='+', help='Run a command on the service')

    env = subcmd.add_parser('env', help='Manipulate application environments') \
        .add_subparsers(dest='subcmd')
    env_show = env.add_parser('show', help='Show the current environment')
    env_list = env.add_parser('list', help='List the environments')
    env_create = env.add_parser('create', help='Create a new environment')
    env_create.add_argument('name', help='Name of the new environment')
    env_destroy = env.add_parser('destroy', help='Destroy an environment')
    env_destroy.add_argument('name', help='Name of the environment to destroy')
    env_switch = env.add_parser('switch', help='Switch to an environment')
    env_switch.add_argument('name', help='Name of the environment')

    push = subcmd.add_parser('push', help='Push the code')
    push.add_argument('--clean', action='store_true', help='clean build')

    var = subcmd.add_parser('var', help='Manipulate application variables') \
        .add_subparsers(dest='subcmd')
    var_list = var.add_parser('list', help='List the application variables')
    var_set = var.add_parser('set', help='Set new application variables')
    var_set.add_argument('values', help='Application variables to set',
                         metavar='key=value', nargs='*')
    var_unset = var.add_parser('unset', help='Unset application variables')
    var_unset.add_argument('variables', help='Application ariables to unset', metavar='var', nargs='*')

    scale = subcmd.add_parser('scale', help='Scale services')
    scale.add_argument('services', nargs='*', metavar='service=count',
                       help='Number of instances to set for each service e.g. www=2')

    restart = subcmd.add_parser('restart', help='Restart the service')
    restart.add_argument('service', help='Specify the service')

    alias = subcmd.add_parser('alias', help='Manage aliases for the service')
    alias.add_argument('commands', nargs='*')

    return parser
    


