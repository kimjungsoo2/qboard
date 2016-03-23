import os
import yaml
from fabric.api import env
from fabric.context_managers import cd
from fabric.contrib.project import rsync_project
from fabric.operations import run, local


class CommandTemplate:
    TERMINATE_PID = 'kill {0}'
    SSH_PASS = 'sshpass -p {0} ssh {1}@{2}'
    GET_RUNNING_PID = 'ps -ef | grep {0} | grep -v grep | awk \'{{print $2}}\''
    GRUNT = "{0} 'nohup grunt --gruntfile {1}/Gruntfile.js serve --force' &"
    PYTHON = "{0} 'nohup /usr/bin/python {1}/manage.py runserver 0.0.0.0:8000' &"
    IMPORT_JIRA_DATA = 'python import.py -d {0}'


with open('fabfile.yaml', 'r') as f:
    CONFIG = yaml.load(f)

LOCAL_PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
REMOTE_PROJECT_DIR = CONFIG['target_directory']

BACKEND_PROJECT_DIRECTORY = "{0}/{1}".format(REMOTE_PROJECT_DIR, CONFIG['path_to_backend_directory'])
FRONTEND_PROJECT_DIRECTORY = "{0}/{1}".format(REMOTE_PROJECT_DIR, CONFIG['path_to_frontend_directory'])


def dev():
    __set_hosts('dev')


def live():
    __set_hosts('live')


def import_jira_data():
    with cd(BACKEND_PROJECT_DIRECTORY):
        run(CommandTemplate.IMPORT_JIRA_DATA.format(CONFIG['number_of_jira_import_days']))


def restart_backend():
    ssh_pass_command = CommandTemplate.SSH_PASS.format(env.password, env.user, env.hosts)
    map(lambda process_id: run(CommandTemplate.TERMINATE_PID.format(process_id)), __remote_process_ids('python'))
    local(CommandTemplate.PYTHON.format(ssh_pass_command, BACKEND_PROJECT_DIRECTORY))


def deploy():
    map(lambda process_id: run(CommandTemplate.TERMINATE_PID.format(process_id)), __remote_process_ids('python'))
    map(lambda process_id: run(CommandTemplate.TERMINATE_PID.format(process_id)), __remote_process_ids('grunt'))

    print('------------------------------------STARTING DEPLOYMENT------------------------------------')
    print('DEPLOY USER\t\t: {0}'.format(os.getlogin()))
    print('TARGET HOST\t\t: {0}'.format(env.hosts))
    print('LOCAL SOURCE DIRECTORY\t: {0}'.format(LOCAL_PROJECT_DIR))
    print('TARGET REMOTE DIRECTORY\t: {0}'.format(REMOTE_PROJECT_DIR))
    print('-------------------------------------------------------------------------------------------')
    rsync_project(REMOTE_PROJECT_DIR, LOCAL_PROJECT_DIR, exclude=(CONFIG['sync_exclusions']), delete=True)

    backend_commands = CONFIG['back_end_commands']
    if backend_commands is not None:
        with cd(BACKEND_PROJECT_DIRECTORY):  # run all commands on backend project directory
            [run(command) for command in backend_commands]

    frontend_commands = CONFIG['front_end_commands']
    if frontend_commands is not None:
        with cd(FRONTEND_PROJECT_DIRECTORY):  # run all commands on frontend project directory
            [run(command) for command in frontend_commands]

    # setup sshpass command to start angular and django application
    ssh_pass_command = CommandTemplate.SSH_PASS.format(env.password, env.user, env.hosts)

    start_angular_cmd = CommandTemplate.GRUNT.format(ssh_pass_command, FRONTEND_PROJECT_DIRECTORY)
    start_django_cmd = CommandTemplate.PYTHON.format(ssh_pass_command, BACKEND_PROJECT_DIRECTORY)

    # run remote process in daemon
    local(start_django_cmd)
    local(start_angular_cmd)


def __remote_process_ids(process_name):
    return run('ps -ef | grep {0} | grep -v grep | awk \'{{print $2}}\''.format(process_name)).split()


def __set_hosts(environment):
    env_info = CONFIG['environment'][environment]
    env.user = env_info['user']
    env.hosts = env_info['host']
    env.password = env_info['password']
